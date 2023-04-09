# tasks

import logging, time, random, json
from mytasks import loadEnvironment as bpmEnv
from locust import task, tag, SequentialTaskSet
from json import JSONDecodeError

#-------------------------------------------
# BPM types

class BpmTask:
    id : str = None
    subject : str = None
    status : str = None

    def __init__(self, id, subject, status):
        self.id = id
        self.subject = subject
        self.status = status

    def getId(self):
        return self.id

    def getSubject(self):
        return self.subject
    
    def getStatus(self):
        return self.status

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

def _buildTaskList(tasksCount, tasksList):

    logging.debug("build tasks - tasksCount %s, taskListLen %d", tasksCount, len(tasksList))

    bpmTaksItems = []
    while len(tasksList) > 0:
        bpmTask = tasksList.pop()
        bpmTaksItems.append(BpmTask(bpmTask["TASK.TKIID"], bpmTask["TAD_DISPLAY_NAME"], bpmTask["STATUS"]))

    bpmTaskList = BpmTaskList(len(bpmTaksItems), bpmTaksItems)
    return bpmTaskList

def _listAvailableTasks(self):
    if self.user.loggedIn == True:
        logging.info("list available tasks, user %s", self.user.userCreds.getName())

        # query task list
        params = {'organization': 'byTask',
                  'shared': 'false',
                  'conditions': [{ 'field': 'taskActivityType', 'operator': 'Equals', 'value': 'USER_TASK' }],
                  'fields': [ 'taskSubject', 'taskStatus', 'assignedToRoleDisplayName'],
                  'aliases': [], 
                  'interaction': 'available', 
                  'size': 25 }
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
                    # print(response.json()) 
                    size = response.json()["size"]
                    items = response.json()["items"]
                    return _buildTaskList(size, items)
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'size' or 'items'")
        return None
    pass

def _listClaimedTasks(self):
    if self.loggedIn == True:
        logging.info("list claimed tasks, user %s", self.userCreds.getName())
    pass

def _taskGetData(self, taskId):
    if self.loggedIn == True:
        logging.info("task get data, user %s, task %s", self.userCreds.getName(), taskId)
    pass

def _taskSetData(self, taskId, payload):
    if self.loggedIn == True:
        logging.info("task set data, user %s, task %s, payload %s", self.userCreds.getName(), taskId, payload)
    pass

def _taskComplete(self, taskId, payload):
    if self.loggedIn == True:
        logging.info("task complete, user %s, task %s, payload %s", self.userCreds.getName(), taskId, payload)

        # test
        with self.client.get("/test", catch_response=True) as response:
            # logging.info("status code: %s", response.status_code)
            if response.status_code == 200:
                try:
                    if response.json()["id"] != "id1":                        
                        response.failure("Did not get expected value in response")
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'greeting'")


    pass

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
                        logging.info("*** logged in user %s", userName)
                    else:
                        logging.error("*** ERROR failed login for user %s", userName)
        pass

    def claim(self):
        if self.user.loggedIn == True:
            taskList : BpmTaskList = _listAvailableTasks(self)

            if taskList.getCount() > 0:
                idx : int = random.randint(0, taskList.getCount()-1)
                bpmTask : BpmTask = taskList.getTasks()[idx];
                taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTask.getStatus()+"]"
                logging.info("Claimed task, user %s, task %s", self.user.userCreds.getName(), taskInfo )
            else:
                 logging.info("No task to claim, user %s", self.user.userCreds.getName() )
        pass

    def complete(self):
        if self.user.loggedIn == True:
            _listClaimedTasks(self.user)

            think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
            logging.info("working on task, user %s", self.user.userCreds.getName())
            time.sleep( think )            
            
            _taskComplete(self.user, "1", "{}")
            logging.info("complete task, user %s", self.user.userCreds.getName())
        pass

    # you can still use the tasks attribute to specify a list of tasks
    tasks = [login, claim, complete]

