# tasks

import logging, time, random, json
from locust import task, tag, SequentialTaskSet
from json import JSONDecodeError
from mytasks import loadEnvironment as bpmEnv
from configurations import payloadManager as bpmPayloadManager
import urllib.parse
from locust.exception import RescheduleTaskImmediately

#-------------------------------------------
# BPM types

class BpmTask:
    id : str = None
    subject : str = None
    status : str = None
    role: str = None

    def __init__(self, id, subject, status, role):
        self.id = id
        self.subject = subject
        self.status = status
        self.role = role

    def getId(self):
        return self.id

    def getSubject(self):
        return self.subject
    
    def getStatus(self):
        return self.status
    
    def getRole(self):
        return self.role

    pass

class BpmTaskList:
    count : int = 0
    bpmTasks : BpmTask = None

    def __init__(self, count, bpmTasks):
        self.count = count
        self.bpmTasks = bpmTasks

    def getCount(self):
        return self.count

    def getTasks(self):
        return self.bpmTasks
    
    pass

#-------------------------------------------
# bpm authentication tokens

# IAM address (cp-console)
def _accessToken(self, baseHost, userName, userPassword):
    access_token : str = None
    params : str = "grant_type=password&scope=openid&username="+userName+"&password="+userPassword
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    with self.client.post(url=baseHost+"/idprovider/v1/auth/identitytoken", data=params, headers=my_headers, catch_response=True) as response:
        logging.debug("_accessToken status code: %s", response.status_code)
        if response.status_code == 200:
            try:
                access_token = response.json()["access_token"]                
            except JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            except KeyError:
                    response.failure("Response did not contain expected key 'access_token'")
    return access_token

# CP4BA address (cpd-cp4ba)
def _cp4baToken(self, baseHost, userName, iamToken):
    cp4ba_token : str = None
    my_headers = {'username': userName, 'iam-token': iamToken }
    
    with self.client.get(url=baseHost+"/v1/preauth/validateAuth", headers=my_headers, catch_response=True) as response:
        logging.debug("_cp4baToken status code: %s", response.status_code)
        if response.status_code == 200:
            try:
                cp4ba_token = response.json()["accessToken"]                
            except JSONDecodeError:
                    response.failure("Response could not be decoded as JSON")
            except KeyError:
                    response.failure("Response did not contain expected key 'greeting'")
    return cp4ba_token

#-------------------------------------------
# bpm logic
# self = MyUser

def _buildTaskList(self, tasksCount, tasksList, interaction):

    logging.debug("build tasks - tasksCount %s, taskListLen %d", tasksCount, len(tasksList))

    isClaiming = False
    if interaction == "available":
         isClaiming = True
    bpmTaksItems = []
    while len(tasksList) > 0:
        bpmTask = tasksList.pop()
        bpmTaskId = bpmTask["TASK.TKIID"]
        bpmStatus = bpmTask["STATUS"]
        bpmSubject = bpmTask["TAD_DISPLAY_NAME"]
        bpmRole = bpmTask["ASSIGNED_TO_ROLE_DISPLAY_NAME"]
        if bpmRole != None and isClaiming == True:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(BpmTask(bpmTaskId, bpmSubject, bpmStatus, bpmRole))
        if bpmRole == None and isClaiming == False:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(BpmTask(bpmTaskId, bpmSubject, bpmStatus, bpmRole))

    bpmTaskList = BpmTaskList(len(bpmTaksItems), bpmTaksItems)
    return bpmTaskList

def _listTasks(self, interaction, size):
    if self.user.loggedIn == True:
        # query task list
        params = {'organization': 'byTask',
                  'shared': 'false',
                  'conditions': [{ 'field': 'taskActivityType', 'operator': 'Equals', 'value': 'USER_TASK' }],
                  'fields': [ 'taskSubject', 'taskStatus', 'assignedToRoleDisplayName'],
                  'aliases': [], 
                  'interaction': interaction, 
                  'size': size }
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        constParams : str = "calcStats=false&includeAllIndexes=false&includeAllBusinessData=false&avoidBasicAuthChallenge=true"
        offset = "0"
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        fullUrl = hostUrl+"/pfs/rest/bpm/federated/v1/tasks?"+constParams+"&offset="+offset
        with self.client.put(url=fullUrl, headers=my_headers, data=json.dumps(params), catch_response=True) as response:
            logging.debug("task list available status code: %s", response.status_code)
            if response.status_code == 200:
                try:
                    rsp = response.json()
                    if logging.DEBUG >= logging.root.level: 
                        logging.debug("task list [%s]", interaction, json.dumps(rsp, indent = 2))
                    size = rsp["size"]
                    items = rsp["items"]
                    logging.debug("list available tasks, user %s, size %d, list %d", self.user.userCreds.getName(), size, len(items))
                    return _buildTaskList(self, size, items, interaction)
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'size' or 'items'")
        return None
    pass

def _taskGetData(self, taskId):
    if self.user.loggedIn == True:
        logging.info("task get data, user %s, task %s", self.userCreds.getName(), taskId)
    pass

def _taskSetData(self, taskId, payload):
    if self.user.loggedIn == True:
        logging.info("task set data, user %s, task %s, payload %s", self.userCreds.getName(), taskId, payload)
    pass

# !!!! /bas/ da parametrizzare
def _taskClaim(self, bpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        taskId = bpmTask.getId()
        fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=assign&toMe=true&parts=none"
        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            logging.debug("task claimed status code: %s", response.status_code)
            rsp = response.json()
            # print(rsp)
            if response.status_code == 200:
                bpmRequestStatus = ""
                bpmTaskState = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        data = rsp["data"]
                        bpmTaskState = data["state"]
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTaskState+"]"
                        logging.info("Claimed task, user %s, task %s", self.user.userCreds.getName(), taskInfo )
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("Claim error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), taskId, bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data.state'")
            else:
                if response.status_code == 401:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("Claim error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), taskId, response.status_code, bpmErrorMessage)
                
    pass

# !!!! /bas/ da parametrizzare
def _taskComplete(self, bpmTask, payload):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        taskId = bpmTask.getId()
        jsonStr = json.dumps(payload)
        fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=complete&parts=none&params="+jsonStr
        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            logging.debug("task completed status code: %s", response.status_code)
            rsp = response.json()
            # print(rsp)
            if response.status_code == 200:
                bpmRequestStatus = ""
                bpmTaskState = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        data = rsp["data"]
                        bpmTaskState = data["state"]
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTaskState+"]"
                        logging.info("Completed task, user %s, task %s", self.user.userCreds.getName(), taskId )
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("Complete error, user %s, task %s, task status %s, task role %s, request status %s, error %s", self.user.userCreds.getName(), taskId, bpmTask.getStatus(), bpmTask.getRole(), bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data.state'")
            else:
                if response.status_code == 401:
                    # print("COMPLETE ERR on task ", taskId, self.user.userCreds.getName(), self.user.completeFailed )
                    # self.user.completeFailed.append(taskId)
                    response.success()
                    # response._manual_result = False
                    # raise RescheduleTaskImmediately() 
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("Complete error, user %s, task %s, task status %s, task role %s, status %d, error %s", self.user.userCreds.getName(), taskId, bpmTask.getStatus(), bpmTask.getRole(), response.status_code, bpmErrorMessage)

    pass

def _buildPayload(taskSubject):
    payload = bpmPayloadManager.buildPayloadForSubject(taskSubject)
    return payload

#-------------------------------------------
class SequenceOfBpmTasks(SequentialTaskSet):
    def login(self):
        if self.user.loggedIn == False:
            uName = "n/a"
            if self.user.userCreds != None:

                userName : str = self.user.userCreds.getName()
                userPassword : str = self.user.userCreds.getPassword()
                iamUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
                hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)

                access_token : str = _accessToken(self, iamUrl, userName, userPassword)
                if access_token != None:
                    self.user.authorizationBearerToken = _cp4baToken(self, hostUrl, userName, access_token)
                    if self.user.authorizationBearerToken != None:
                        self.user.loggedIn = True
                        logging.debug("Logged in user %s", userName)
                    else:
                        logging.error("*** ERROR failed login for user %s", userName)
        pass

    def claim(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "available", 25)
            if taskList != None and taskList.getCount() > 0:
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];
                _taskClaim(self, bpmTask)
            else:
                logging.info("No task to claim, user %s", self.user.userCreds.getName() )
        pass

    def complete(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];

                # think time
                taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTask.getStatus()+"]"
                think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                logging.info("Working on task, user %s, task %s", self.user.userCreds.getName(), taskInfo)
                # time.sleep( think )

                payload = _buildPayload(bpmTask.getSubject())
                _taskComplete(self, bpmTask, payload)

            else:
                logging.info("No task to complete, user %s", self.user.userCreds.getName() )
        pass

    # you can still use the tasks attribute to specify a list of tasks
    tasks = [login, claim, complete]

