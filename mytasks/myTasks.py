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
    state: str = None
    role: str = None
    variableNames = []
    actions = []
    data: dict = None

    def __init__(self, id, subject, status, state, role):
        self.id = id
        self.subject = subject
        self.status = status
        self.state = state
        self.role = role

    def getId(self):
        return self.id

    def getSubject(self):
        return self.subject
    
    def getStatus(self):
        return self.status
    
    def getState(self):
        return self.state
    def setState(self, state):
        self.state = state
    
    def getRole(self):
        return self.role

    def getVariableNames(self):
        return self.variableNames
    def setVariableNames(self, variableNames):
        self.variableNames = variableNames

    def getActions(self):
        return self.actions
    def setActions(self, actions):
        self.actions = actions
    def hasAction(self, action):
        for act in self.actions:
            if act == action:
                return True
        return False
    
    def setTaskData(self, data):
        self.data = data
    def getTaskData(self):
        return self.data

    def buildListOfVarNames(self):
        paramVarNames = ""
        allNames = self.getVariableNames()
        totNames = len(allNames)
        for pName in allNames:
            paramVarNames = paramVarNames + pName
            totNames = totNames - 1
            if totNames > 0:
                paramVarNames = paramVarNames + ","
        return paramVarNames
    
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

def _getAttributeNamesFromDictionary(varDict):
    listOfVarNames = []
    varNames : dict = varDict.keys()
    for attrName in varDict.keys():
        listOfVarNames.append(attrName)
    return listOfVarNames

def _cleanVarData(varDict):
    listOfVarNames = _getAttributeNamesFromDictionary(varDict)
    for vn in listOfVarNames:
        vnObj = varDict[vn]
        del vnObj["@metadata"]
    return varDict

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
                bpmTaksItems.append(BpmTask(bpmTaskId, bpmSubject, bpmStatus, None, bpmRole))
        if bpmRole == None and isClaiming == False:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(BpmTask(bpmTaskId, bpmSubject, bpmStatus, None, bpmRole))

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
                        logging.debug("task list [%s] %s", interaction, json.dumps(rsp, indent = 2))
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

def _taskGetDetails(self, bpmTask : BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        taskId = bpmTask.getId()
        fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?parts=data,actions"
        with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:
            logging.debug("task get details status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                rsp = response.json()
                if logging.DEBUG >= logging.root.level: 
                    logging.debug("task details taskId[%s] %s", taskId, json.dumps(rsp, indent = 2))
                
                bpmRequestStatus = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        data1 = rsp["data"]
                        
                        #actions = data1["actions"]

                        data2 = data1["data"]
                        # variables = data2["variables"]

                        bpmTask.setActions(data1["actions"])
                        bpmTask.setVariableNames(_getAttributeNamesFromDictionary(data2["variables"]))

                        return True
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("Task details error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), taskId, bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data'")
            else:
                if response.status_code == 401:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("Task get details error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), taskId, response.status_code, bpmErrorMessage)

    return False

def _taskGetData(self, bpmTask: BpmTask):
    if self.user.loggedIn == True:
        if _taskGetDetails(self, bpmTask) == True:
            authValue : str = "Bearer "+self.user.authorizationBearerToken
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
            hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            taskId = bpmTask.getId()
            paramNames = bpmTask.buildListOfVarNames()
            fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=getData&fields="+paramNames
            with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:
                logging.debug("task get data status code: %s", response.status_code)
                rsp = response.json()
                if response.status_code == 200:
                    rsp = response.json()
                    if logging.DEBUG >= logging.root.level: 
                        logging.debug("task data taskId[%s] %s", taskId, json.dumps(rsp, indent = 2))
                    
                    bpmRequestStatus = ""
                    bpmErrorMessage = ""
                    try:                                        
                        bpmRequestStatus = rsp["status"]
                        if bpmRequestStatus == "200":
                            data = rsp["data"]
                            bpmTask.setTaskData(_cleanVarData(data["resultMap"]))
                            return True
                        else:
                            data = rsp["Data"]
                            bpmErrorMessage = data["errorMessage"]
                            logging.error("Task details error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), taskId, bpmRequestStatus, bpmErrorMessage)
                            pass
                    
                    except JSONDecodeError:
                            response.failure("Response could not be decoded as JSON")
                    except KeyError:
                            response.failure("Response did not contain expected key 'status' or 'data'")
                else:
                    if response.status_code == 401:
                        response.success()
                    data = rsp["Data"]
                    bpmErrorMessage = data["errorMessage"]
                    logging.error("Task get details error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), taskId, response.status_code, bpmErrorMessage)
    return False

def _taskSetData(self, bpmTask, payload):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        taskId = bpmTask.getId()
        jsonStr = json.dumps(payload)
        fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=setData&params="+jsonStr
        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            logging.debug("task set data status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                bpmRequestStatus = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        data = rsp["data"]
                        bpmTask.setTaskData(_cleanVarData(data["resultMap"]))              
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject() +"]"
                        logging.info("Updated task, user %s, task %s", self.user.userCreds.getName(), taskId )
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("Update error, user %s, task %s, task status %s, task role %s, request status %s, error %s", self.user.userCreds.getName(), taskId, bpmTask.getStatus(), bpmTask.getRole(), bpmRequestStatus, bpmErrorMessage)
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
                logging.error("Update error, user %s, task %s, task status %s, task role %s, status %d, error %s", self.user.userCreds.getName(), taskId, bpmTask.getStatus(), bpmTask.getRole(), response.status_code, bpmErrorMessage)

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
def _taskRelease(self, bpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        taskId = bpmTask.getId()
        fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=assign&back=true&parts=none"
        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            logging.debug("task release status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                bpmRequestStatus = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ "]"
                        logging.info("Released task, user %s, task %s", self.user.userCreds.getName(), taskInfo )
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("Release error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), taskId, bpmRequestStatus, bpmErrorMessage)
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
                logging.error("Release error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), taskId, response.status_code, bpmErrorMessage)
                
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
    def bawlogin(self):
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

    def bawClaimTask(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "available", 25)
            if taskList != None and taskList.getCount() > 0:
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];

                if _taskGetDetails(self, bpmTask) == True:
                    if logging.DEBUG >= logging.root.level: 
                        logging.debug("TASK [%s] DETAIL BEFORE CLAIM actions[%s] variables[%s]", bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                    if bpmTask.hasAction("ACTION_CLAIM"):
                        _taskClaim(self, bpmTask)

                        if logging.DEBUG >= logging.root.level: 
                            if _taskGetDetails(self, bpmTask) == True:
                                logging.debug("TASK [%s] DETAIL AFTER CLAIM actions[%s] variables[%s]", bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())
                    else:
                        if logging.DEBUG >= logging.root.level: 
                            logging.indebugfo("TASK [%s] CONFLICT, cannot claim task, actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("No task to claim, user %s", self.user.userCreds.getName() )
        pass

    def bawCompleteTask(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];

                if _taskGetDetails(self, bpmTask) == True:
                    if logging.DEBUG >= logging.root.level: 
                        logging.debug("TASK [%s] DETAIL BEFORE COMPLETE actions[%s] variables[%s]", bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                    if bpmTask.hasAction("ACTION_COMPLETE"):
                        # think time
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTask.getStatus()+"]"
                        think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                        logging.info("Working on task, user %s, task %s", self.user.userCreds.getName(), taskInfo)
                        time.sleep( think )
 
                        payload = _buildPayload(bpmTask.getSubject())
                        _taskComplete(self, bpmTask, payload)
                    else:
                        if logging.DEBUG >= logging.root.level: 
                            logging.indebugfo("TASK [%s] CONFLICT, cannot complete already claimed task, actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("No task to complete, user %s", self.user.userCreds.getName() )
        pass

    def bawGetTaskData(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];
                _taskGetData(self, bpmTask)
                if logging.DEBUG >= logging.root.level: 
                    logging.debug("TASK [%s] CLEANED TASK DATA %s", bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))

        pass

    def bawSetTaskData(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];

                if _taskGetDetails(self, bpmTask) == True:
                    if logging.DEBUG >= logging.root.level: 
                        logging.debug("TASK [%s] DETAIL BEFORE SET DATA actions[%s] data[%s]", bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))

                    if bpmTask.hasAction("ACTION_SETTASK"):
                        # think time
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTask.getStatus()+"]"
                        think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                        logging.info("Postponing on task, user %s, task %s", self.user.userCreds.getName(), taskInfo)
                        time.sleep( think )
 
                        payload = _buildPayload(bpmTask.getSubject())
                        _taskSetData(self, bpmTask, payload)
                        if logging.DEBUG >= logging.root.level: 
                            logging.debug("TASK [%s] UPDATED TASK DATA %s", bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))
                    else:
                        if logging.DEBUG >= logging.root.level: 
                            logging.debug("TASK [%s] HAS NO ACTION_SETTASK, available actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("No task to set data, user %s", self.user.userCreds.getName() )

        pass

    def bawReleaseTask(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];

                if _taskGetDetails(self, bpmTask) == True:
                    if logging.DEBUG >= logging.root.level: 
                        logging.debug("TASK [%s] DETAIL BEFORE RELEASE actions[%s] data[%s]", bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))
                    if bpmTask.hasAction("ACTION_CANCELCLAIM"):
                        _taskRelease(self, bpmTask)
                        if logging.DEBUG >= logging.root.level: 
                            logging.debug("TASK [%s] RELEASED ", bpmTask.getId())
                    else:
                        if logging.DEBUG >= logging.root.level: 
                            logging.debug("TASK [%s] HAS NO ACTION_CANCELCLAIM, available actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("No task to release, user %s", self.user.userCreds.getName() )
        pass

    # you can still use the tasks attribute to specify a list of tasks
    tasks = [bawlogin, bawClaimTask, bawCompleteTask, bawGetTaskData, bawSetTaskData, bawReleaseTask]

