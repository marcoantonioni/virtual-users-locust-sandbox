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

class BpmFederatedSystem:
    restUrlPrefix : str = None # /bas/rest/bpm/wle
    systemID : str = None
    displayName : str = None
    systemType : str = None # SYSTEM_TYPE_WLE
    id : str = None
    taskCompletionUrlPrefix : str = None # /bas/teamworks
    version : str = None
    indexRefreshInterval : int = 0
    statusCode : str = None

    def __init__(self, restUrlPrefix, systemID, displayName, systemType, id, taskCompletionUrlPrefix, version, indexRefreshInterval, statusCode):
        self.restUrlPrefix = restUrlPrefix
        self.systemID = systemID
        self.displayName = displayName
        self.systemType = systemType
        self.id = id
        self.taskCompletionUrlPrefix = taskCompletionUrlPrefix
        self.version = version
        self.indexRefreshInterval = indexRefreshInterval
        self.statusCode = statusCode

    def getSystemID(self):
        return self.systemID

    def getRestUrlPrefix(self):
        return self.restUrlPrefix

    def getStatusCode(self):
        return self.statusCode


class BpmTask:
    id : str = None
    subject : str = None
    status : str = None
    state: str = None
    role: str = None
    systemID: str = None
    variableNames = []
    actions = []
    data: dict = None
    federatedSystem : BpmFederatedSystem = None

    def __init__(self, id, subject, status, state, role, systemID):
        self.id = id
        self.subject = subject
        self.status = status
        self.state = state
        self.role = role
        self.systemID = systemID

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

    def getSystemID(self):
        return self.systemID

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

    def setFederatedSystem(self, fedSys):
        self.federatedSystem = fedSys
    def getFederatedSystem(self):
        return self.federatedSystem
    def isFederatedSystem(self):
        return self.federatedSystem != None

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
    bpmFederatedSystems = dict()

    def __init__(self, count, bpmTasks):
        self.count = count
        self.bpmTasks = bpmTasks

    def getCount(self):
        return self.count

    def getTasks(self):
        return self.bpmTasks
    
    def getPreparedTask( self, idx ):
        bpmTask : BpmTask = self.getTasks()[idx];
        if bpmTask != None:
            bpmTask.setFederatedSystem(self.bpmFederatedSystems[bpmTask.getSystemID()])
        return bpmTask
    
    def getPreparedTaskRandom(self):
        idx : int = random.randint(0, self.getCount()-1)
        return self.getPreparedTask( idx )
    
    def setFederationInfos( self, listOfBpmSystems ):
        for bpmSystem in listOfBpmSystems:
            bpmFedSys : BpmFederatedSystem = BpmFederatedSystem(bpmSystem["restUrlPrefix"], bpmSystem["systemID"], bpmSystem["displayName"], bpmSystem["systemType"], bpmSystem["id"], bpmSystem["taskCompletionUrlPrefix"], bpmSystem["version"], bpmSystem["indexRefreshInterval"], bpmSystem["statusCode"])
            self.bpmFederatedSystems[bpmFedSys.getSystemID()] = bpmFedSys


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
        if logging.getLogger().isEnabledFor(logging.DEBUG):
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
        if logging.getLogger().isEnabledFor(logging.DEBUG):
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

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("_buildTaskList - tasksCount %s, taskListLen %d", tasksCount, len(tasksList))

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
        bpmSystemID = bpmTask["systemID"]
        if bpmRole != None and isClaiming == True:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(BpmTask(bpmTaskId, bpmSubject, bpmStatus, None, bpmRole, bpmSystemID))
        if bpmRole == None and isClaiming == False:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(BpmTask(bpmTaskId, bpmSubject, bpmStatus, None, bpmRole, bpmSystemID))

    bpmTaskList = BpmTaskList(len(bpmTaksItems), bpmTaksItems)
    return bpmTaskList

def _listTasks(self, interaction, size):

    uriBaseTaskList = ""
    taskListFederated = False
    taskListStrategy = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_TASK_LIST_STRATEGY)
    if taskListStrategy == bpmEnv.BpmEnvironment.valBAW_TASK_LIST_STRATEGY_FEDERATEDPORTAL:
        taskListFederated = True
        uriBaseTaskList = "/pfs/rest/bpm/federated/v1/tasks"
    else:
        baseUri = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
        if baseUri == None:
            baseUri = ""
        uriBaseTaskList = baseUri+"/rest/bpm/wle/v1/tasks"

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
        fullUrl = hostUrl+uriBaseTaskList+"?"+constParams+"&offset="+offset
        with self.client.put(url=fullUrl, headers=my_headers, data=json.dumps(params), catch_response=True) as response:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_listTasks '%s' status code: %s", interaction, response.status_code)
            if response.status_code == 200:
                try:
                    rsp = response.json()
                    size = rsp["size"]
                    items = rsp["items"]
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("_listTasks [%s] user %s, size %d, numtasks %d, response %s", interaction, self.user.userCreds.getName(), size, len(items), json.dumps(rsp, indent = 2))

                    _taskList : BpmTaskList = _buildTaskList(self, size, items, interaction)
                    if taskListFederated == True:
                        _taskList.setFederationInfos(rsp["federationResult"])
                        
                    return _taskList
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        logging.error("_listTasks error, user %s, esponse did not contain expected key 'size', 'items', if federated portal [now is %s] 'federationResult'", self.user.userCreds.getName(), taskListFederated)
                        response.failure("Response did not contain expected key 'size', 'items', if federated portal 'federationResult'")
        return None
    pass

# !!!! /bas/ da parametrizzare
def _buildTaskUrl(bpmTask : BpmTask, user):
    fullUrl = ""
    if bpmTask.isFederatedSystem():
        fullUrl = bpmTask.getFederatedSystem().getRestUrlPrefix()+"/v1/task/"+bpmTask.getId()
    else:
        hostUrl : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+bpmTask.getId()
    return fullUrl

def _taskGetDetails(self, bpmTask : BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        #hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        #taskId = bpmTask.getId()
        #fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?parts=data,actions"

        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?parts=data,actions"
        
        with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_taskGetDetails status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                rsp = response.json()
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("_taskGetDetails taskId[%s] %s", bpmTask.getId(), json.dumps(rsp, indent = 2))
                
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
                        logging.error("_taskGetDetails error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data'")
            else:
                if response.status_code == 401 or response.status_code == 409:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("Task get details error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), bpmTask.getId(), response.status_code, bpmErrorMessage)

    return False

def _taskGetData(self, bpmTask: BpmTask):
    if self.user.loggedIn == True:
        if _taskGetDetails(self, bpmTask) == True:
            authValue : str = "Bearer "+self.user.authorizationBearerToken
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

            #hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            #taskId = bpmTask.getId()
            #paramNames = bpmTask.buildListOfVarNames()
            #fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=getData&fields="+paramNames

            paramNames = bpmTask.buildListOfVarNames()
            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=getData&fields="+paramNames

            with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("_taskGetData status code: %s", response.status_code)
                rsp = response.json()
                if response.status_code == 200:
                    rsp = response.json()
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("_taskGetData taskId[%s] %s", bpmTask.getId(), json.dumps(rsp, indent = 2))
                    
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
                            logging.error("_taskGetData error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmRequestStatus, bpmErrorMessage)
                            pass
                    
                    except JSONDecodeError:
                            response.failure("Response could not be decoded as JSON")
                    except KeyError:
                            response.failure("Response did not contain expected key 'status' or 'data'")
                else:
                    if response.status_code == 401 or response.status_code == 409:
                        response.success()
                    data = rsp["Data"]
                    bpmErrorMessage = data["errorMessage"]
                    logging.error("_taskGetData error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), bpmTask.getId(), response.status_code, bpmErrorMessage)
    return False

def _taskSetData(self, bpmTask, payload):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        #hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        #taskId = bpmTask.getId()
        #jsonStr = json.dumps(payload)
        #fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=setData&params="+jsonStr

        jsonStr = json.dumps(payload)
        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=setData&params="+jsonStr

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_taskSetData status code: %s", response.status_code)
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
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("_taskSetData, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                        return True
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("_taskSetData error, user %s, task %s, task status %s, task role %s, request status %s, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getStatus(), bpmTask.getRole(), bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data.state'")
            else:
                if response.status_code == 401 or response.status_code == 409:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("_taskSetData error, user %s, task %s, task status %s, task role %s, status %d, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getStatus(), bpmTask.getRole(), response.status_code, bpmErrorMessage)
    return False

def _taskClaim(self, bpmTask : BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=assign&toMe=true&parts=none"

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_taskClaim status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                bpmRequestStatus = ""                
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        data = rsp["data"]
                        bpmTaskState = data["state"]
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTaskState+"]"
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("_taskClaim, user %s, task %s", self.user.userCreds.getName(), taskInfo )
                        return True
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("_taskClaim error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data.state'")
            else:
                if response.status_code == 401 or response.status_code == 409:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("_taskClaim error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), bpmTask.getId(), response.status_code, bpmErrorMessage)
    return False                

def _taskRelease(self, bpmTask: BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=assign&back=true&parts=none"

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_taskRelease status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                bpmRequestStatus = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ "]"
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("_taskRelease, user %s, task %s", self.user.userCreds.getName(), taskInfo )
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("_taskRelease error, user %s, task %s, request status %s, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data.state'")
            else:
                if response.status_code == 401 or response.status_code == 409:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("_taskRelease error, user %s, task %s, status %d, error %s", self.user.userCreds.getName(), bpmTask.getId(), response.status_code, bpmErrorMessage)
                
    pass

def _taskComplete(self, bpmTask, payload):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        #hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        #taskId = bpmTask.getId()
        #fullUrl = hostUrl+"/bas/rest/bpm/wle/v1/task/"+taskId+"?action=complete&parts=none&params="+jsonStr
        
        jsonStr = json.dumps(payload)
        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=complete&parts=none&params="+jsonStr

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_taskComplete status code: %s", response.status_code)
            rsp = response.json()
            if response.status_code == 200:
                bpmRequestStatus = ""
                bpmErrorMessage = ""
                try:                                        
                    bpmRequestStatus = rsp["status"]
                    if bpmRequestStatus == "200":
                        data = rsp["data"]
                        bpmTaskState = data["state"]
                        taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+ " - "+bpmTaskState+"]"
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("_taskComplete, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                        return True
                    else:
                        data = rsp["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("_taskComplete error, user %s, task %s, task status %s, task role %s, request status %s, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getStatus(), bpmTask.getRole(), bpmRequestStatus, bpmErrorMessage)
                        pass
                
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'status' or 'data.state'")
            else:
                if response.status_code == 401 or response.status_code == 409:
                    response.success()
                data = rsp["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("_taskComplete error, user %s, task %s, task status %s, task role %s, status %d, error %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getStatus(), bpmTask.getRole(), response.status_code, bpmErrorMessage)
    return False

def _buildPayload(taskSubject):
    payload = bpmPayloadManager.buildPayloadForSubject(taskSubject)
    return payload

#-------------------------------------------
class SequenceOfBpmTasks(SequentialTaskSet):
    def bawLogin(self):
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
                        logging.info("User[%s] - bawLogin - logged in", userName)
                    else:
                        logging.error("***ERROR*** User[%s] - bawLogin - failed login", userName)
        pass

    def bawClaimTask(self):
        if self.user.loggedIn == True:
            taskList : BpmTaskList = _listTasks(self, "available", 25)
            if taskList != None and taskList.getCount() > 0:
                bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                if _taskGetDetails(self, bpmTask) == True:

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("bawClaimTask TASK [%s] DETAIL BEFORE CLAIM actions[%s] variables[%s]", bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                    if bpmTask.hasAction("ACTION_CLAIM"):
                        if _taskClaim(self, bpmTask) == True:
                            logging.info("User[%s] - bawClaimTask - claimed task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            if _taskGetDetails(self, bpmTask) == True:
                                logging.debug("bawClaimTask TASK [%s] DETAIL AFTER CLAIM actions[%s] variables[%s]", bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())
                    else:
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("bawClaimTask TASK [%s] CONFLICT, cannot claim task, actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("User[%s] - bawClaimTask no task to claim", self.user.userCreds.getName() )
        pass

    def bawCompleteTask(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                if _taskGetDetails(self, bpmTask) == True:

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("bawCompleteTask TASK [%s] DETAIL BEFORE COMPLETE actions[%s] variables[%s]", bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                    if bpmTask.hasAction("ACTION_COMPLETE"):
                        # think time
                        think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                        logging.info("User[%s] - bawCompleteTask working on task[%s] for think time %d", self.user.userCreds.getName(), bpmTask.getId(), think)
                        time.sleep( think )
 
                        payload = _buildPayload(bpmTask.getSubject())
                        if _taskComplete(self, bpmTask, payload) == True:
                            logging.info("User[%s] - bawCompleteTask - completed task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                    else:
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("bawCompleteTask TASK [%s] CONFLICT, cannot complete already claimed task, actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("User[%s] - bawCompleteTask no task to complete", self.user.userCreds.getName() )
        pass

    def bawGetTaskData(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                if _taskGetData(self, bpmTask) == True:
                    logging.info("User[%s] - bawGetTaskData - got data from task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("bawGetTaskData TASK [%s] CLEANED TASK DATA %s", bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))

            else:
                logging.info("User[%s] - bawGetTaskData no task to set data", self.user.userCreds.getName() )
        pass

    def bawSetTaskData(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                if _taskGetDetails(self, bpmTask) == True:

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("bawSetTaskData TASK [%s] DETAIL BEFORE SET DATA actions[%s] data[%s]", bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))

                    if bpmTask.hasAction("ACTION_SETTASK"):
                        # think time
                        think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                        logging.info("User[%s] - bawSetTaskData working on task[%s] for think time %d", self.user.userCreds.getName(), bpmTask.getId(), think)
                        time.sleep( think )
 
                        payload = _buildPayload(bpmTask.getSubject())
                        if _taskSetData(self, bpmTask, payload) == True:
                            logging.info("User[%s] - bawSetTaskData - set data and postponed on task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("bawSetTaskData TASK [%s] UPDATED TASK DATA %s", bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))
                    else:
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("bawSetTaskData TASK [%s] HAS NO ACTION_SETTASK, available actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("User[%s] - bawSetTaskData no task to set data", self.user.userCreds.getName() )

        pass

    def bawReleaseTask(self):
        if self.user.loggedIn == True:
            taskList = _listTasks(self, "claimed", 25)

            if taskList != None and taskList.getCount() > 0:    
                bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                if _taskGetDetails(self, bpmTask) == True:

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("bawReleaseTask TASK [%s] DETAIL BEFORE RELEASE actions[%s] data[%s]", bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))
                    
                    if bpmTask.hasAction("ACTION_CANCELCLAIM"):
                        if _taskRelease(self, bpmTask) == True:
                            logging.info("User[%s] - bawReleaseTask - released task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("bawReleaseTask TASK [%s] RELEASED ", bpmTask.getId())
                    else:
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("bawReleaseTask TASK [%s] HAS NO ACTION_CANCELCLAIM, available actions %s", bpmTask.getId(), bpmTask.getActions())

            else:
                logging.info("User[%s] - bawReleaseTask no task to release", self.user.userCreds.getName() )
        pass

    # you can still use the tasks attribute to specify a list of tasks
    tasks = [bawLogin, bawClaimTask, bawCompleteTask, bawGetTaskData, bawSetTaskData, bawReleaseTask]

