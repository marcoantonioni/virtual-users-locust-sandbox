# tasks

import logging, time, random, json
from json import JSONDecodeError
from base64 import b64encode
from locust import task, tag, SequentialTaskSet
from mytasks.processInstanceManager import BpmProcessInstanceManager as bpmPIM
from mytasks.processInstanceManager import BpmProcessInstance as bpmPI
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys 
from bawsys import bawRestResponseManager as responseMgr 

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

def _extractPayloadOptionalThinkTime(payloadInfos: dict, user, wait: bool):
    payload = payloadInfos["jsonObject"]
    if wait == True:
        think : int = payloadInfos["thinkTime"]
        if ( think == -1):
            think : int = random.randint(user.min_think_time, user.max_think_time)
        time.sleep( think )
    return payload

def _buildTaskUrl(bpmTask : bawSys.BpmTask, user):
    fullUrl = ""
    if bpmTask.isFederatedSystem():
        fullUrl = bpmTask.getFederatedSystem().getRestUrlPrefix()+"/v1/task/"+bpmTask.getId()
    else:
        hostUrl : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri : str = user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
        fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/task/"+bpmTask.getId()
    return fullUrl

def _basicAuthHeader(username, password):
    username = username.encode("latin1")
    password = password.encode("latin1")
    return "Basic " + b64encode(b":".join((username, password))).strip().decode("ascii")


#-------------------------------------------

class SequenceOfBpmTasks(SequentialTaskSet):

    #==========================================================
    # Supporting functions
    #==========================================================

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
        return self.user.verbose

    def idleUser(self):
        if self.user.idleNotify == True:
            self.user.idleCounter += 1
            if self.user.idleCounter > self.user.maxIdleLoops:
                self.user.idleCounter = 0
                logging.info("User[%s] - idle ...", self.user.userCreds.getName() )

    def nothingToDo(self, message: str):
        if self.isVerboseEnabled() == True:
            logging.info("User[%s] - %s", self.user.userCreds.getName(), message )
        else:
            self.idleUser()

    def _buildPayload(self, taskSubject, preExistPayload = None):
        return self.user._payload(taskSubject, preExistPayload)

    def _prepareHeaders(self):
        _headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.user.runningTraditional == False:
            _headers['Authorization'] = 'Bearer '+self.user.authorizationBearerToken
        else:
            _headers['Authorization'] = _basicAuthHeader(self.user.userCreds.getName(), self.user.userCreds.getPassword())
        return _headers

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

    #==========================================================
    # Task supporting functions
    #==========================================================

    def _taskClaim(self, bpmTask : bawSys.BpmTask):
        if self.user.loggedIn == True:

            # headers and authentication
            my_headers = self._prepareHeaders()

            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=assign&toMe=true&parts=none"

            with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskClaim", response, self.user.userCreds.getName(), bpmTask, [401, 409])

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
            my_headers = self._prepareHeaders()

            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=assign&back=true&parts=none"

            with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskRelease", response, self.user.userCreds.getName(), bpmTask, [401, 409])

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
            my_headers = self._prepareHeaders()

            jsonStr = json.dumps(payload)
            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=complete&parts=none&params="+jsonStr

            with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskComplete", response, self.user.userCreds.getName(), bpmTask, [401, 409])

                if restResponseManager.getStatusCode() == 200:
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        data = restResponseManager.getObject("data")
                        bpmTaskState = data["state"]
                        logging.debug("_taskComplete, user %s, task %s, state %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTaskState )
                    return True

        return False

    def _taskGetDetails(self, bpmTask : bawSys.BpmTask):
        if self.user.loggedIn == True:

            # headers and authentication 
            my_headers = self._prepareHeaders()

            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?parts=data,actions"
            
            with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskGetDetails", response, self.user.userCreds.getName(), bpmTask, [401, 409])

                if restResponseManager.getStatusCode() == 200:
                    data1 = restResponseManager.getObject("data")
                    data2 = data1["data"]
                    bpmTask.setActions(data1["actions"])
                    bpmTask.setVariableNames(_getAttributeNamesFromDictionary(data2["variables"]))

                    return True

        return False

    def _taskGetData(self, bpmTask: bawSys.BpmTask):
        if self.user.loggedIn == True:
            if self._taskGetDetails(bpmTask) == True:

                # headers and authentication 
                my_headers = self._prepareHeaders()

                paramNames = bpmTask.buildListOfVarNames()
                fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=getData&fields="+paramNames

                with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:

                    restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskGetData", response, self.user.userCreds.getName(), bpmTask, [401, 409])

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
            my_headers = self._prepareHeaders()

            jsonStr = json.dumps(payload)
            fullUrl = _buildTaskUrl(bpmTask, self.user) + "?action=setData&params="+jsonStr

            with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskSetData", response, self.user.userCreds.getName(), bpmTask, [401, 409])

                if restResponseManager.getStatusCode() == 200:
                    data = restResponseManager.getObject("data")
                    bpmTask.setTaskData(_cleanVarData(data["resultMap"]))

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("_taskSetData, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                    return True

        return False

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
            my_headers = self._prepareHeaders()
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
                
                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_listTasks", response, self.user.userCreds.getName(), None, [401, 409])

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

                        _taskList : bawSys.BpmTaskList = self._buildTaskList(size, items, interaction)
                        
                        if taskListFederated == True:
                            _taskList.setFederationInfos(restResponseManager.getObject("federationResult"))
                        
                    return _taskList
            return None

    #==========================================================
    # Task functions
    #==========================================================
    
    def bawLogin(self):        
        if self.user.loggedIn == False:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_LOGIN ):
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
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_CLAIM ):
                taskList : bawSys.BpmTaskList = self._listTasks("available", 25)
                if taskList != None and taskList.getCount() > 0:
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if self._taskGetDetails(bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawClaimTask TASK [%s] DETAIL BEFORE CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(),bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                        if bpmTask.hasAction("ACTION_CLAIM"):
                            if self._taskClaim(bpmTask) == True:
                                self.user.idleCounter = 0
                                logging.info("User[%s] - bawClaimTask - claimed task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                if self._taskGetDetails(bpmTask) == True:
                                    logging.debug("bawClaimTask TASK [%s] DETAIL AFTER CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawClaimTask TASK [%s] CONFLICT, cannot claim task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    self.nothingToDo("bawClaimTask no task to claim")

    def bawCompleteTask(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_COMPLETE ):
                taskList = self._listTasks("claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if self._taskGetDetails(bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawCompleteTask TASK [%s] DETAIL BEFORE COMPLETE actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())

                        if bpmTask.hasAction("ACTION_COMPLETE"):

                            if self._taskGetData(bpmTask) == True:

                                payloadInfos = self._buildPayload(bpmTask.getSubject(), bpmTask.getTaskData() )

                                payload = _extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
                                logging.info("User[%s] - bawCompleteTask working on task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                                if self._taskComplete(bpmTask, payload) == True:
                                    self.user.idleCounter = 0
                                    logging.info("User[%s] - bawCompleteTask - completed task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                            else:
                                if logging.getLogger().isEnabledFor(logging.DEBUG):
                                    logging.debug("User[%s] - bawCompleteTask TASK [%s] ERROR, cannot _taskGetData, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawCompleteTask TASK [%s] CONFLICT, cannot complete already claimed task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    self.nothingToDo("bawCompleteTask no task to complete")

    def bawGetTaskData(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_GETDATA ):
                taskList = self._listTasks("claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if self._taskGetData(bpmTask) == True:
                        self.user.idleCounter = 0
                        logging.info("User[%s] - bawGetTaskData - got data from task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("User[%s] - bawGetTaskData TASK [%s] CLEANED TASK DATA %s", self.user.userCreds.getName(), bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))

                else:
                    self.nothingToDo("bawGetTaskData no task to set data")

    def bawSetTaskData(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_SETDATA ):
                taskList = self._listTasks("claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if self._taskGetDetails(bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawSetTaskData TASK [%s] DETAIL BEFORE SET DATA actions[%s] data[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))

                        if bpmTask.hasAction("ACTION_SETTASK"):

                            if self._taskGetData(bpmTask) == True:

                                payloadInfos = self._buildPayload(bpmTask.getSubject(), bpmTask.getTaskData())

                                payload = _extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
                                logging.info("User[%s] - bawSetTaskData working on task[%s]", self.user.userCreds.getName(), bpmTask.getId())
                                if self._taskSetData(bpmTask, payload) == True:
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
                    self.nothingToDo("bawSetTaskData no task to set data to")

    def bawReleaseTask(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_RELEASE ):
                taskList = self._listTasks("claimed", 25)

                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()

                    if self._taskGetDetails(bpmTask) == True:

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawReleaseTask TASK [%s] DETAIL BEFORE RELEASE actions[%s] data[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), json.dumps(bpmTask.getTaskData(), indent = 2))
                        
                        if bpmTask.hasAction("ACTION_CANCELCLAIM"):
                            if self._taskRelease(bpmTask) == True:
                                self.user.idleCounter = 0
                                logging.info("User[%s] - bawReleaseTask - released task[%s]", self.user.userCreds.getName(), bpmTask.getId())

                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] RELEASED ", self.user.userCreds.getName(), bpmTask.getId())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] HAS NO ACTION_CANCELCLAIM, available actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())

                else:
                    self.nothingToDo("bawReleaseTask no task to release")

    def bawCreateInstance(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS ):
                pem = self.user.getEPM()
                pim = self.user.getPIM()
                processInfo: bawSys.BpmExposedProcessInfo = pem.nextRandomProcessInfos()
                processName = processInfo.getAppProcessName()
                jsonPayloadInfos = self._buildPayload("Start-"+processName)
                jsonPayload = _extractPayloadOptionalThinkTime(jsonPayloadInfos, self.user, True)
                strPayload = json.dumps(jsonPayload)
                my_headers = self._prepareHeaders()
                processInstanceInfo : bpmPI = pim.createInstance(self.user.getEnvironment(), self.user.runningTraditional, self.user.userCreds.getName(), processInfo, strPayload, my_headers)
                if processInstanceInfo != None:
                    logging.info("User[%s] - bawCreateInstance - process name[%s] - process id[%s], state[%s]", self.user.userCreds.getName(), processName, processInstanceInfo.getPiid(), processInstanceInfo.getState())

    #==========================================================
    # List of enabled tasks
    #==========================================================
    tasks = [bawLogin, bawCreateInstance, bawClaimTask, bawCompleteTask, bawGetTaskData, bawSetTaskData, bawReleaseTask]

