# tasks

import logging, time, random, json
from json import JSONDecodeError
from base64 import b64encode
from locust import task, tag, SequentialTaskSet
from mytasks.processInstanceManager import BpmProcessInstanceManager as bpmPIM
from mytasks.processInstanceManager import BpmProcessInstance as bpmPI
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys 

#-------------------------------------------
    

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
# bpm logic

class RestResponseManager:
    contextName = None
    response = None
    userName = None
    bpmTask = None
    ignoreCodes = None
    js = None

    def __init__(self, contextName, response, userName, bpmTask, ignoreCodes):
        self.contextName = contextName
        self.response = response
        self.userName = userName
        self.bpmTask = bpmTask
        self.ignoreCodes = ignoreCodes
        self.js = {}
        self.isJsObj = False
        try:
            self.js = response.json()
            #print(json.dumps(self.js, indent=2))
            self.isJsObj = True
        except:
            logging.error("%s, status code [%s], error text [%s], empty/not-valid json content", contextName, response.status_code, response.text)

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("%s status code: %s", contextName, response.status_code)
        if response.status_code >= 300:
            ignoreCode = False
            # ignore codes in list
            for rc in ignoreCodes:
                if response.status_code == rc:
                    ignoreCode = True
                    response.success()
            taskId = ""
            taskSubject = ""
            taskData = None
            if self.bpmTask != None:
                taskId = self.bpmTask.getId()
                taskSubject = self.bpmTask.getSubject()
                taskData = self.bpmTask.getTaskData()
            data = None
            bpmErrorMessage = self.response.text
            if self.isJsObj == True:
                try:
                    try:
                        data = self.js["Data"]
                        bpmErrorMessage = data["errorMessage"]
                    except KeyError:
                        pass

                    if ignoreCode == False:
                        logging.error("%s error, user %s, task %s, subject '%s', status %d, error %s", self.contextName, self.userName, taskId, taskSubject, self.response.status_code, bpmErrorMessage)
                        if taskData != None:
                            logging.error("%s error, user %s, task %s, payload %s", self.contextName, self.userName, taskId, json.dumps(taskData))

                except JSONDecodeError:
                    logging.error("%s error, user %s, task %s, subject '%s', response could not be decoded as JSON", self.contextName, self.userName, taskId, taskSubject)
                    self.response.failure("Response could not be decoded as JSON")
                except KeyError:
                    logging.error("%s error, user %s, task %s, subject '%s', response did not contain expected key 'Data', 'errorMessage'", self.contextName, self.userName, taskId, taskSubject)
                    self.response.failure("Response did not contain expected key 'Data', 'errorMessage'")

    def getJson(self):
        return self.js
    
    def getStatusCode(self):
        return self.response.status_code
    
    def getObject(self, key: str):
        try:
            if self.isJsObj == True:
                return self.js[key]
            else:
                return None
        except JSONDecodeError:
            logging.error("%s error, user %s, response could not be decoded as JSON", self.contextName, self.userName)
            self.response.failure("Response could not be decoded as JSON")
        except KeyError:
            logging.error("%s error, user %s, response did not contain expected key '%s'", self.contextName, self.userName, key)
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
        bpmSystemID = ""
        try:
            bpmSystemID = bpmTask["systemID"]
        except:
            pass
        if bpmRole != None and isClaiming == True:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(bawSys.BpmTask(bpmTaskId, bpmSubject, bpmStatus, None, bpmRole, bpmSystemID))
        if bpmRole == None and isClaiming == False:             
            if self.user.isSubjectForUser(bpmSubject) == True:
                bpmTaksItems.append(bawSys.BpmTask(bpmTaskId, bpmSubject, bpmStatus, None, bpmRole, bpmSystemID))

    return bawSys.BpmTaskList(len(bpmTaksItems), bpmTaksItems)

def _basicAuthHeader(username, password):
    username = username.encode("latin1")
    password = password.encode("latin1")
    return "Basic " + b64encode(b":".join((username, password))).strip().decode("ascii")

def _prepareHeaders(self):
    _headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    if self.user.runningTraditional == False:
        _headers['Authorization'] = 'Bearer '+self.user.authorizationBearerToken
    else:
        _headers['Authorization'] = _basicAuthHeader(self.user.userCreds.getName(), self.user.userCreds.getPassword())
    return _headers

def _listTasks(self, interaction, size):
    if self.user.loggedIn == True:

        # set constants
        uriBaseTaskList = ""
        taskListFederated = False
        hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        processAppName = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)

        # query task list
        offset = "0"
        constParams : str = "calcStats=false&includeAllIndexes=false&includeAllBusinessData=false&avoidBasicAuthChallenge=true"
        params = {'organization': 'byTask',
                  'shared': 'false',
                  'conditions': [{ 'field': 'taskActivityType', 'operator': 'Equals', 'value': 'USER_TASK' }],
                  'fields': [ 'taskSubject', 'taskStatus', 'assignedToRoleDisplayName'],
                  'aliases': [], 
                  'interaction': interaction, 
                  'size': size }

        # headers and authentication
        my_headers = _prepareHeaders(self)
        if self.user.runningTraditional == False:
            taskListFederated = True
            uriBaseTaskList = "/pfs/rest/bpm/federated/v1/tasks"
        else:
            baseUri = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            if baseUri == None:
                baseUri = ""
            uriBaseTaskList = baseUri+"/rest/bpm/wle/v1/tasks"

        fullUrl = hostUrl+uriBaseTaskList+"?"+constParams+"&offset="+offset+"&processAppName="+processAppName

        with self.client.put(url=fullUrl, headers=my_headers, data=json.dumps(params), catch_response=True) as response:
            
            restResponseManager: RestResponseManager = RestResponseManager("_listTasks", response, self.user.userCreds.getName(), None, [401, 409])

            if restResponseManager.getStatusCode() == 200:
                _taskList = None
                size = 0
                items = None
                if self.user.runningTraditional == False:
                    size = restResponseManager.getObject("size")
                    items = restResponseManager.getObject("items")
                else:
                    data = restResponseManager.getObject("data")
                    size = data["size"]
                    try:
                        items = data["items"]
                    except KeyError:
                        pass

                if items != None:
                    # print(json.dumps(items, indent=2))

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("_listTasks [%s] user %s, size %d, numtasks %d, response %s", interaction, self.user.userCreds.getName(), size, len(items), json.dumps(restResponseManager.getJson(), indent = 2))

                    _taskList : bawSys.BpmTaskList = _buildTaskList(self, size, items, interaction)
                    
                    if taskListFederated == True:
                        _taskList.setFederationInfos(restResponseManager.getObject("federationResult"))
                    
                return _taskList
        return None
    pass

def _buildTaskUrl(bpmTask : bawSys.BpmTask, user):
    fullUrl = ""
    if bpmTask.isFederatedSystem():
        fullUrl = bpmTask.getFederatedSystem().getRestUrlPrefix()+"/v1/task/"+bpmTask.getId()
    else:
        hostUrl : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
        fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/task/"+bpmTask.getId()
    return fullUrl

def _taskGetDetails(self, bpmTask : bawSys.BpmTask):
    if self.user.loggedIn == True:

        # headers and authentication 
        my_headers = _prepareHeaders(self)

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

def _taskGetData(self, bpmTask: bawSys.BpmTask):
    if self.user.loggedIn == True:
        if _taskGetDetails(self, bpmTask) == True:

            # headers and authentication 
            my_headers = _prepareHeaders(self)

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

def _taskSetData(self, bpmTask: bawSys.BpmTask, payload):
    if self.user.loggedIn == True:

        # headers and authentication 
        my_headers = _prepareHeaders(self)

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

def _taskClaim(self, bpmTask : bawSys.BpmTask):
    if self.user.loggedIn == True:

        # headers and authentication
        my_headers = _prepareHeaders(self)

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

def _taskRelease(self, bpmTask: bawSys.BpmTask):
    if self.user.loggedIn == True:

        # headers and authentication 
        my_headers = _prepareHeaders(self)

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

def _taskComplete(self, bpmTask: bawSys.BpmTask, payload):
    if self.user.loggedIn == True:

        # headers and authentication 
        my_headers = _prepareHeaders(self)

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

def isVerboseEnabled(self):
    verbose = False
    strVerbose : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_VU_VERBOSE)
    if strVerbose != None:
        verbose = strVerbose.lower() == "true"
    return verbose

def idleUser(self):
    if self.user.idleNotify == True:
        self.user.idleCounter += 1
        if self.user.idleCounter > self.user.maxIdleLoops:
            self.user.idleCounter = 0
            logging.info("User[%s] - idle ...", self.user.userCreds.getName() )

#-------------------------------------------

class SequenceOfBpmTasks(SequentialTaskSet):
        
    def _buildPayload(self, taskSubject, preExistPayload = None):
        return self.user._payload(taskSubject, preExistPayload)

    def bawLogin(self):        
        if self.user.loggedIn == False:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_LOGIN ):
                uName = "n/a"
                if self.user.userCreds != None:
                    self.user.loggedIn = False
                    self.user.cookieTraditional = None
                    self.user.authorizationBearerToken = None

                    userName = self.user.userCreds.getName()
                    userPassword = self.user.userCreds.getPassword()    

                    if self.user.runningTraditional == True:
                        self.user.cookieTraditional = bawSys._loginTraditional(self.user.getEnvironment(), userName, userPassword)
                        if self.user.cookieTraditional != None:
                            self.user.loggedIn = True
                    else:
                        self.user.authorizationBearerToken = bawSys._loginZen(self.user.getEnvironment(), userName, userPassword)
                        if self.user.authorizationBearerToken != None:
                            self.user.loggedIn = True

                    if self.user.loggedIn == True:
                        self.user.idleCounter = 0
                        logging.info("User[%s] - bawLogin - logged in", userName)
                    else:
                        logging.error("User[%s] - bawLogin - failed login", userName)


    def bawClaimTask(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_CLAIM ):
                taskList : bawSys.BpmTaskList = _listTasks(self, "available", 25)
                if taskList != None and taskList.getCount() > 0:
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawClaimTask TASK [%s] DETAIL BEFORE CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(),bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                        if bpmTask.hasAction("ACTION_CLAIM"):
                            if _taskClaim(self, bpmTask) == True:
                                self.user.idleCounter = 0
                                logging.info("User[%s] - bawClaimTask - claimed task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                if _taskGetDetails(self, bpmTask) == True:
                                    logging.debug("bawClaimTask TASK [%s] DETAIL AFTER CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawClaimTask TASK [%s] CONFLICT, cannot claim task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    if isVerboseEnabled(self) == True:
                        logging.info("User[%s] - bawClaimTask no task to claim", self.user.userCreds.getName() )
                    else:
                        idleUser(self)

    def bawCompleteTask(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_COMPLETE ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawCompleteTask TASK [%s] DETAIL BEFORE COMPLETE actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                        if bpmTask.hasAction("ACTION_COMPLETE"):

                            if _taskGetData(self, bpmTask) == True:

                                payloadInfos = self._buildPayload(bpmTask.getSubject(), bpmTask.getTaskData() )

                                payload = _extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
                                logging.info("User[%s] - bawCompleteTask working on task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                                if _taskComplete(self, bpmTask, payload) == True:
                                    self.user.idleCounter = 0
                                    logging.info("User[%s] - bawCompleteTask - completed task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                            else:
                                if logging.getLogger().isEnabledFor(logging.DEBUG):
                                    logging.debug("User[%s] - bawCompleteTask TASK [%s] ERROR, cannot _taskGetData, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawCompleteTask TASK [%s] CONFLICT, cannot complete already claimed task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    if isVerboseEnabled(self) == True:
                        logging.info("User[%s] - bawCompleteTask no task to complete", self.user.userCreds.getName() )
                    else:
                        idleUser(self)

    def bawGetTaskData(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_GETDATA ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetData(self, bpmTask) == True:
                        self.user.idleCounter = 0
                        logging.info("User[%s] - bawGetTaskData - got data from task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("User[%s] - bawGetTaskData TASK [%s] CLEANED TASK DATA %s", self.user.userCreds.getName(), bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))

                else:
                    if isVerboseEnabled(self) == True:
                        logging.info("User[%s] - bawGetTaskData no task to set data", self.user.userCreds.getName() )
                    else:
                        idleUser(self)

    def bawSetTaskData(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_SETDATA ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawSetTaskData TASK [%s] DETAIL BEFORE SET DATA actions[%s] data[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))

                        if bpmTask.hasAction("ACTION_SETTASK"):

                            if _taskGetData(self, bpmTask) == True:

                                payloadInfos = self._buildPayload(bpmTask.getSubject(), bpmTask.getTaskData())

                                payload = _extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
                                logging.info("User[%s] - bawSetTaskData working on task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                                if _taskSetData(self, bpmTask, payload) == True:
                                    self.user.idleCounter = 0
                                    logging.info("User[%s] - bawSetTaskData - set data and postponed on task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                                if logging.getLogger().isEnabledFor(logging.DEBUG):
                                    logging.debug("User[%s] - bawSetTaskData TASK [%s] UPDATED TASK DATA %s", self.user.userCreds.getName(), bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))
                            else:
                                if logging.getLogger().isEnabledFor(logging.DEBUG):
                                    logging.debug("User[%s] - bawSetTaskData TASK [%s] ERROR, cannot _taskGetData, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())
                        
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawSetTaskData TASK [%s] HAS NO ACTION_SETTASK, available actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    if isVerboseEnabled(self) == True:
                        logging.info("User[%s] - bawSetTaskData no task to set data", self.user.userCreds.getName() )
                    else:
                        idleUser(self)

    def bawReleaseTask(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_RELEASE ):
                taskList = _listTasks(self, "claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if _taskGetDetails(self, bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawReleaseTask TASK [%s] DETAIL BEFORE RELEASE actions[%s] data[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))
                        
                        if bpmTask.hasAction("ACTION_CANCELCLAIM"):
                            if _taskRelease(self, bpmTask) == True:
                                self.user.idleCounter = 0
                                logging.info("User[%s] - bawReleaseTask - released task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] RELEASED ", self.user.userCreds.getName(), bpmTask.getId())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] HAS NO ACTION_CANCELCLAIM, available actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    if isVerboseEnabled(self) == True:
                        logging.info("User[%s] - bawReleaseTask no task to release", self.user.userCreds.getName() )
                    else:
                        idleUser(self)

    def bawCreateInstance(self):
        if self.user.loggedIn == True:
            if isActionEnabled( self, bpmEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS ):
                pem = self.user.getEPM()
                pim = self.user.getPIM()
                processInfo: bawSys.BpmExposedProcessInfo = pem.nextRandomProcessInfos()
                processName = processInfo.getAppProcessName()
                jsonPayloadInfos = self._buildPayload("Start-"+processName)
                jsonPayload = _extractPayloadOptionalThinkTime(jsonPayloadInfos, self.user, True)
                strPayload = json.dumps(jsonPayload)
                my_headers = _prepareHeaders(self)
                processInstanceInfo : bpmPI = pim.createInstance(self.user.getEnvironment(), self.user.runningTraditional, self.user.userCreds.getName(), processInfo, strPayload, my_headers)
                if processInstanceInfo != None:
                    logging.info("User[%s] - bawCreateInstance - process name[%s] - process id[%s], state[%s]", self.user.userCreds.getName(), processName, processInstanceInfo.getPiid(), processInstanceInfo.getState())

    # list of enabled tasks
    tasks = [bawLogin, bawCreateInstance, bawClaimTask, bawCompleteTask, bawGetTaskData, bawSetTaskData, bawReleaseTask]

