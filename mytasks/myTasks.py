# tasks

import logging, time, random, json
from locust import task, tag, SequentialTaskSet
from locust.exception import RescheduleTaskImmediately
from json import JSONDecodeError
from mytasks.processInstanceManager import BpmProcessInstanceManager as bpmPIM
from mytasks.processInstanceManager import BpmProcessInstance as bpmPI
from bawsys import loadEnvironment as bpmEnv

#-------------------------------------------
# BPM types

class BpmFederatedSystem:
    restUrlPrefix : str = None # /...server-base-uri.../rest/bpm/wle
    systemID : str = None
    displayName : str = None
    systemType : str = None # SYSTEM_TYPE_WLE | SYSTEM_TYPE_CASE
    id : str = None
    taskCompletionUrlPrefix : str = None # /...server-base-uri.../teamworks
    version : str = None
    indexRefreshInterval : int = 0
    statusCode : str = None
    targetObjectStoreName : str = None # present only if systemType==SYSTEM_TYPE_CASE

    def __init__(self, restUrlPrefix, systemID, displayName, systemType, id, taskCompletionUrlPrefix, version, indexRefreshInterval, statusCode, targetObjectStoreName):
        self.restUrlPrefix = restUrlPrefix
        self.systemID = systemID
        self.displayName = displayName
        self.systemType = systemType
        self.id = id
        self.taskCompletionUrlPrefix = taskCompletionUrlPrefix
        self.version = version
        self.indexRefreshInterval = indexRefreshInterval
        self.statusCode = statusCode
        self.targetObjectStoreName = targetObjectStoreName

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
            targetObjectStoreName = None
            systemType = bpmSystem["systemType"]
            if systemType == "SYSTEM_TYPE_CASE":
                targetObjectStoreName = bpmSystem["targetObjectStoreName"]
            bpmFedSys : BpmFederatedSystem = BpmFederatedSystem(bpmSystem["restUrlPrefix"], bpmSystem["systemID"], bpmSystem["displayName"], systemType, bpmSystem["id"], bpmSystem["taskCompletionUrlPrefix"], bpmSystem["version"], bpmSystem["indexRefreshInterval"], bpmSystem["statusCode"], targetObjectStoreName)
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
        if vnObj != None:
            try:
                del vnObj["@metadata"]
            except KeyError:
                pass
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
                logging.error("_accessToken error, user %s, response could not be decoded as JSON", userName)
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                logging.error("_accessToken error, user %s, did not contain expected key 'access_token'", userName)
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
                logging.error("_cp4baToken error, user %s, response could not be decoded as JSON", userName)
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                logging.error("_cp4baToken error, user %s, did not contain expected key 'accessToken'", userName)
                response.failure("Response did not contain expected key 'accessToken'")
    return cp4ba_token

#-------------------------------------------
# bpm logic

class RestResponseManager:
    contextName = None
    response = None
    userName = None
    taskId = None
    ignoreCodes = None
    js = None

    def __init__(self, contextName, response, userName, taskId, ignoreCodes):
        self.contextName = contextName
        self.response = response
        self.userName = userName
        self.taskId = taskId
        self.ignoreCodes = ignoreCodes
        self.js = {}
        try:
            self.js = response.json()
        except:
            logging.error("%s status code: %s, empty/not-valid json content", contextName, response.status_code)

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("%s status code: %s", contextName, response.status_code)
        if response.status_code >= 300:
            # ignore codes in list
            for rc in ignoreCodes:
                if response.status_code == rc:
                    response.success()
            try:
                data = self.js["Data"]
                bpmErrorMessage = data["errorMessage"]
                logging.error("%s error, user %s, status %d, error %s", self.contextName, self.userName, self.response.status_code, bpmErrorMessage)
            except JSONDecodeError:
                logging.error("%s error, user %s, response could not be decoded as JSON", self.contextName, self.user.userCreds.getName())
                self.response.failure("Response could not be decoded as JSON")
            except KeyError:
                logging.error("%s error, user %s, response did not contain expected key 'Data', 'errorMessage'", self.contextName, self.user.userCreds.getName())
                self.response.failure("Response did not contain expected key 'Data', 'errorMessage'")

    def getJson(self):
        return self.js
    
    def getStatusCode(self):
        return self.response.status_code
    
    def getObject(self, key: str):
        try:
            return self.js[key]
        except JSONDecodeError:
            logging.error("%s error, user %s, response could not be decoded as JSON", self.contextName, self.user.userCreds.getName())
            self.response.failure("Response could not be decoded as JSON")
        except KeyError:
            logging.error("%s error, user %s, response did not contain expected key '%s'", self.contextName, self.user.userCreds.getName(), key)
            self.response.failure("Response did not contain expected key '"+key+"'")
        return None
    

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

    return BpmTaskList(len(bpmTaksItems), bpmTaksItems)

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
        processAppName = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)

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

        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        fullUrl = hostUrl+uriBaseTaskList+"?"+constParams+"&offset="+offset+"&processAppName="+processAppName
        
        with self.client.put(url=fullUrl, headers=my_headers, data=json.dumps(params), catch_response=True) as response:

            restResponseManager: RestResponseManager = RestResponseManager("_listTasks", response, self.user.userCreds.getName(), None, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                size = restResponseManager.getObject("size")
                items = restResponseManager.getObject("items")

                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("_listTasks [%s] user %s, size %d, numtasks %d, response %s", interaction, self.user.userCreds.getName(), size, len(items), json.dumps(restResponseManager.getJson(), indent = 2))

                _taskList : BpmTaskList = _buildTaskList(self, size, items, interaction)
                
                if taskListFederated == True:
                    _taskList.setFederationInfos(restResponseManager.getObject("federationResult"))
                    
                return _taskList
        return None
    pass

def _buildTaskUrl(bpmTask : BpmTask, user):
    fullUrl = ""
    if bpmTask.isFederatedSystem():
        fullUrl = bpmTask.getFederatedSystem().getRestUrlPrefix()+"/v1/task/"+bpmTask.getId()
    else:
        hostUrl : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
        fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/task/"+bpmTask.getId()
    return fullUrl

def _taskGetDetails(self, bpmTask : BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?parts=data,actions"
        
        with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:

            restResponseManager: RestResponseManager = RestResponseManager("_taskGetDetails", response, self.user.userCreds.getName(), bpmTask, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                data1 = restResponseManager.getObject("data")
                data2 = data1["data"]
                bpmTask.setActions(data1["actions"])
                bpmTask.setVariableNames(_getAttributeNamesFromDictionary(data2["variables"]))

                return True

    return False

def _taskGetData(self, bpmTask: BpmTask):
    if self.user.loggedIn == True:
        if _taskGetDetails(self, bpmTask) == True:
            authValue : str = "Bearer "+self.user.authorizationBearerToken
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

            paramNames = bpmTask.buildListOfVarNames()
            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=getData&fields="+paramNames

            with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: RestResponseManager = RestResponseManager("_taskGetData", response, self.user.userCreds.getName(), bpmTask, [401, 409])

                if restResponseManager.getStatusCode() == 200:
                    data = restResponseManager.getObject("data")
                    bpmTask.setTaskData(_cleanVarData(data["resultMap"]))

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("_taskGetData, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                    return True

    return False

def _taskSetData(self, bpmTask, payload):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        jsonStr = json.dumps(payload)
        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=setData&params="+jsonStr

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

            restResponseManager: RestResponseManager = RestResponseManager("_taskSetData", response, self.user.userCreds.getName(), bpmTask, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                data = restResponseManager.getObject("data")
                bpmTask.setTaskData(_cleanVarData(data["resultMap"]))

                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("_taskSetData, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                return True

    return False

def _taskClaim(self, bpmTask : BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=assign&toMe=true&parts=none"

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

            restResponseManager: RestResponseManager = RestResponseManager("_taskClaim", response, self.user.userCreds.getName(), bpmTask, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    data = restResponseManager.getObject("data")
                    bpmTaskState = data["state"]
                    logging.debug("_taskClaim, user %s, task %s, state %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTaskState )
                return True

    return False                

def _taskRelease(self, bpmTask: BpmTask):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=assign&back=true&parts=none"

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

            restResponseManager: RestResponseManager = RestResponseManager("_taskRelease", response, self.user.userCreds.getName(), bpmTask, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    data = restResponseManager.getObject("data")
                    bpmTaskState = data["state"]
                    logging.debug("_taskRelease, user %s, task %s, state %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTaskState )
                return True

    return False

def _taskComplete(self, bpmTask, payload):
    if self.user.loggedIn == True:
        authValue : str = "Bearer "+self.user.authorizationBearerToken
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        jsonStr = json.dumps(payload)
        fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=complete&parts=none&params="+jsonStr

        with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

            restResponseManager: RestResponseManager = RestResponseManager("_taskComplete", response, self.user.userCreds.getName(), bpmTask, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    data = restResponseManager.getObject("data")
                    bpmTaskState = data["state"]
                    logging.debug("_taskComplete, user %s, task %s, state %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTaskState )
                return True

    return False

def _extractPayloadOptionalThinkTime(payloadInfos: dict, user, wait: bool):
    payload = payloadInfos["jsonObject"]
    if wait == True:
        think : int = payloadInfos["thinkTime"]
        if ( think == -1):
            think : int = random.randint(user.min_think_time, user.max_think_time)
        time.sleep( think )
    return payload

def isActionEnabled(self, key):
    actionEnabled = False
    try:
        if self.user.selectedUserActions != None:
            userAction = self.user.selectedUserActions[key]
            if userAction != None:
                actionEnabled = userAction == bpmEnv.BpmEnvironment.keyBAW_ACTION_ACTIVATED
    except:
        pass
    return actionEnabled

#-------------------------------------------

class SequenceOfBpmTasks(SequentialTaskSet):
        
    def _buildPayload(self, taskSubject):
        return self.user._payload(taskSubject)

    def bawLogin(self):        
        if self.user.loggedIn == False:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_LOGIN ):
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
                            logging.error("User[%s] - bawLogin - failed login ***ERROR***", userName)
        pass

    def bawClaimTask(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_CLAIM ):
                taskList : BpmTaskList = _listTasks(self, "available", 25)
                if taskList != None and taskList.getCount() > 0:
                    bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawClaimTask TASK [%s] DETAIL BEFORE CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(),bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                        if bpmTask.hasAction("ACTION_CLAIM"):
                            if _taskClaim(self, bpmTask) == True:
                                logging.info("User[%s] - bawClaimTask - claimed task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                if _taskGetDetails(self, bpmTask) == True:
                                    logging.debug("bawClaimTask TASK [%s] DETAIL AFTER CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawClaimTask TASK [%s] CONFLICT, cannot claim task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    logging.info("User[%s] - bawClaimTask no task to claim", self.user.userCreds.getName() )
        pass

    def bawCompleteTask(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_COMPLETE ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawCompleteTask TASK [%s] DETAIL BEFORE COMPLETE actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                        if bpmTask.hasAction("ACTION_COMPLETE"):
                            payloadInfos = self._buildPayload(bpmTask.getSubject())
                            payload = _extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
                            logging.info("User[%s] - bawCompleteTask working on task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                            if _taskComplete(self, bpmTask, payload) == True:
                                logging.info("User[%s] - bawCompleteTask - completed task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawCompleteTask TASK [%s] CONFLICT, cannot complete already claimed task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    logging.info("User[%s] - bawCompleteTask no task to complete", self.user.userCreds.getName() )
        pass

    def bawGetTaskData(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_GETDATA ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetData(self, bpmTask) == True:
                        logging.info("User[%s] - bawGetTaskData - got data from task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("User[%s] - bawGetTaskData TASK [%s] CLEANED TASK DATA %s", self.user.userCreds.getName(), bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))

                else:
                    logging.info("User[%s] - bawGetTaskData no task to set data", self.user.userCreds.getName() )
        pass

    def bawSetTaskData(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_SETDATA ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawSetTaskData TASK [%s] DETAIL BEFORE SET DATA actions[%s] data[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))

                        if bpmTask.hasAction("ACTION_SETTASK"):
                            payloadInfos = self._buildPayload(bpmTask.getSubject())
                            payload = _extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
                            logging.info("User[%s] - bawSetTaskData working on task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                            if _taskSetData(self, bpmTask, payload) == True:
                                logging.info("User[%s] - bawSetTaskData - set data and postponed on task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawSetTaskData TASK [%s] UPDATED TASK DATA %s", self.user.userCreds.getName(), bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawSetTaskData TASK [%s] HAS NO ACTION_SETTASK, available actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    logging.info("User[%s] - bawSetTaskData no task to set data", self.user.userCreds.getName() )
        pass

    def bawReleaseTask(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_RELEASE ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawReleaseTask TASK [%s] DETAIL BEFORE RELEASE actions[%s] data[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))
                        
                        if bpmTask.hasAction("ACTION_CANCELCLAIM"):
                            if _taskRelease(self, bpmTask) == True:
                                logging.info("User[%s] - bawReleaseTask - released task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] RELEASED ", self.user.userCreds.getName(), bpmTask.getId())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] HAS NO ACTION_CANCELCLAIM, available actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    logging.info("User[%s] - bawReleaseTask no task to release", self.user.userCreds.getName() )
        pass

    def bawCreateInstance(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS ):
                pem = self.user.getEPM()
                pim = self.user.getPIM()

                #------------------------------
                processInfoKeys = pem.getKeys()
                totalKeys = len(processInfoKeys)
                rndIdx : int = random.randint(0, (totalKeys-1))
                key = processInfoKeys[rndIdx]
                processName = key.split("/")[0]
                processInfo = pem.getProcessInfos(key)  
                jsonPayloadInfos = self._buildPayload("Start-"+processName)
                #------------------------------

                jsonPayload = _extractPayloadOptionalThinkTime(jsonPayloadInfos, self.user, True)
                strPayload = json.dumps(jsonPayload)
                processInstanceInfo : bpmPI = pim.createInstance(self.user.getEnvironment(), processInfo, strPayload, self.user.authorizationBearerToken)
                if processInstanceInfo != None:
                    logging.info("User[%s] - bawCreateInstance - process name[%s] - process id[%s], state[%s]", self.user.userCreds.getName(), processName, processInstanceInfo.getPiid(), processInstanceInfo.getState())
        pass

    # list of enabled tasks
    tasks = [bawLogin, bawClaimTask, bawCompleteTask, bawGetTaskData, bawSetTaskData, bawReleaseTask, bawCreateInstance]

