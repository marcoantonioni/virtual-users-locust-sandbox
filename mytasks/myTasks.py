# tasks

import logging, json
from locust import task, tag, SequentialTaskSet
from bawsys.processInstanceManager import BpmProcessInstanceManager as bpmPIM
from bawsys.processInstanceManager import BpmProcessInstance as bpmPI
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys 
from bawsys import bawRestResponseManager as responseMgr 
from bawsys import bawUtils as bawUtils 


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
            _headers['Authorization'] = bawUtils._basicAuthHeader(self.user.userCreds.getName(), self.user.userCreds.getPassword())
        return _headers

    def _buildTaskUrl(self, bpmTask : bawSys.BpmTask):
        fullUrl = ""
        if bpmTask.isFederatedSystem():
            fullUrl = bpmTask.getFederatedSystem().getRestUrlPrefix()+"/v1/task/"+bpmTask.getId()
        else:
            hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            baseUri : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/task/"+bpmTask.getId()
        return fullUrl

    def _buildTaskList(self, tasksCount, tasksList, interaction):

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("_buildTaskList - tasksCount %s, taskListLen %d", tasksCount, len(tasksList))

        # print(json.dumps(tasksList,indent=2))

        isClaiming = False
        if interaction == "available":
            isClaiming = True

        bpmTaksItems = []
        while len(tasksList) > 0:            
            bpmTask : bawSys.BpmTask = bawSys.BpmTask( tasksList.pop() )
            
            epm = self.user.getExposedProcessManager()
            snapName = epm.getSnapshotName()    
            appAcronym = epm.getAppAcronym()
            if appAcronym == self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM):
                configuredSnapName = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
                strTip = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP)
                useTip = False
                if strTip.lower() == "true":
                    useTip = True
                if configuredSnapName == None or configuredSnapName == "":
                    configuredSnapName = snapName
                    useTip = True
                if snapName == configuredSnapName:
                    selectTask = False
                    # se Tip
                    if bpmTask.getSnapshotName() == None and useTip == True:
                        selectTask = True
                    else:
                        # se snapname
                        if bpmTask.getSnapshotName() != None and bpmTask.getSnapshotName() == configuredSnapName:
                            selectTask = True

                    if selectTask == True:
                        listOfProcessNames = epm.getAppProcessNames()                                        
                        for procName in listOfProcessNames:
                            if procName == bpmTask.getProcessName():
                                if self.user.isSubjectForUser(bpmTask.getSubject()) == True:
                                    if (bpmTask.getRole() != None and isClaiming == True) or (bpmTask.getRole() == None and isClaiming == False):             
                                        bpmTaksItems.append(bpmTask)

        return bawSys.BpmTaskList(len(bpmTaksItems), bpmTaksItems)

    #==========================================================
    # Task supporting functions
    #==========================================================

    def _taskClaim(self, bpmTask : bawSys.BpmTask):
        if self.user.loggedIn == True:
            my_headers = self._prepareHeaders()
            fullUrl = self._buildTaskUrl(bpmTask) + "?action=assign&toMe=true&parts=none"
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
            my_headers = self._prepareHeaders()
            fullUrl = self._buildTaskUrl(bpmTask) + "?action=assign&back=true&parts=none"
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
            my_headers = self._prepareHeaders()
            jsonStr = json.dumps(payload)
            fullUrl = self._buildTaskUrl(bpmTask) + "?action=complete&parts=none&params="+jsonStr
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
            my_headers = self._prepareHeaders()
            fullUrl = self._buildTaskUrl(bpmTask) + "?parts=data,actions"
            with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:
                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskGetDetails", response, self.user.userCreds.getName(), bpmTask, [401, 409])
                if restResponseManager.getStatusCode() == 200:
                    data1 = restResponseManager.getObject("data")
                    data2 = data1["data"]
                    bpmTask.setActions(data1["actions"])
                    bpmTask.setVariableNames(bawUtils._getAttributeNamesFromDictionary(data2["variables"]))

                    return True
        return False

    def _taskGetData(self, bpmTask: bawSys.BpmTask):
        if self.user.loggedIn == True:
            if self._taskGetDetails(bpmTask) == True:                 
                my_headers = self._prepareHeaders()
                paramNames = bpmTask.buildListOfVarNames()
                fullUrl = self._buildTaskUrl(bpmTask) + "?action=getData&fields="+paramNames
                with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:
                    restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskGetData", response, self.user.userCreds.getName(), bpmTask, [401, 409])
                    if restResponseManager.getStatusCode() == 200:
                        data = restResponseManager.getObject("data")
                        bpmTask.setTaskData(bawUtils._cleanVarData(data["resultMap"]))

                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("_taskGetData, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                        return True
        return False

    def _taskSetData(self, bpmTask: bawSys.BpmTask, payload):
        if self.user.loggedIn == True:
            my_headers = self._prepareHeaders()
            jsonStr = json.dumps(payload)
            fullUrl = self._buildTaskUrl(bpmTask) + "?action=setData&params="+jsonStr
            with self.client.put(url=fullUrl, headers=my_headers, catch_response=True) as response:
                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_taskSetData", response, self.user.userCreds.getName(), bpmTask, [401, 409])
                if restResponseManager.getStatusCode() == 200:
                    data = restResponseManager.getObject("data")
                    bpmTask.setTaskData(bawUtils._cleanVarData(data["resultMap"]))
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("_taskSetData, user %s, task %s", self.user.userCreds.getName(), bpmTask.getId() )
                    return True
        return False

    def _listTasks(self, interaction, size):
        if self.user.loggedIn == True:
            uriBaseTaskList = ""
            taskListFederated = False
            hostUrl : str = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            processAppAcronym = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
            
            # query task list
            offset = "0"
            constParams : str = "interaction=claimed_and_available&calcStats=false&includeAllBusinessData=false"

            params = {'organization': 'byTask',
                    'shared': 'false',
                    'conditions': [{ 'field': 'taskActivityType', 'operator': 'Equals', 'value': 'USER_TASK' }],
                    'fields': [ 'taskSubject', 'taskStatus', 'assignedToRoleDisplayName', 'instanceName', 'instanceId', 'instanceStatus', 'instanceProcessApp', 'instanceSnapshot', 'bpdName'],
                    'aliases': [], 
                    'interaction': interaction, 
                    'size': size }
            my_headers = self._prepareHeaders()
            if self.user.runningTraditional == False:
                taskListFederated = True
                uriBaseTaskList = "/pfs/rest/bpm/federated/v1/tasks"
            else:
                baseUri = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
                if baseUri == None:
                    baseUri = ""
                uriBaseTaskList = baseUri+"/rest/bpm/wle/v1/tasks"
            fullUrl = hostUrl+uriBaseTaskList+"?"+constParams+"&offset="+offset+"&processAppName="+processAppAcronym
            with self.client.get(url=fullUrl, headers=my_headers, data=json.dumps(params), catch_response=True) as response:

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
                                payload = bawUtils._extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
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
                                payload = bawUtils._extractPayloadOptionalThinkTime(payloadInfos, self.user, True)
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
                pim = self.user.getPIM()
                if pim.consumeInstance() == True:
                    pem = self.user.getEPM()
                    processInfo: bawSys.BpmExposedProcessInfo = pem.nextRandomProcessInfos()
                    if processInfo != None:
                        processName = processInfo.getAppProcessName()
                        jsonPayloadInfos = self._buildPayload("Start-"+processName)
                        jsonPayload = bawUtils._extractPayloadOptionalThinkTime(jsonPayloadInfos, self.user, True)
                        strPayload = json.dumps(jsonPayload)
                        my_headers = self._prepareHeaders()
                        processInstanceInfo : bpmPI = pim.createInstance(self.user.getEnvironment(), self.user.runningTraditional, self.user.userCreds.getName(), processInfo, strPayload, my_headers)
                        if processInstanceInfo != None:
                            logging.info("User[%s] - bawCreateInstance - process name[%s] - process id[%s], state[%s]", self.user.userCreds.getName(), processName, processInstanceInfo.getPiid(), processInstanceInfo.getState())
                    else:
                        logging.error("User[%s] - bawCreateInstance no process info available", self.user.userCreds.getName())
                else:
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("User[%s] - bawCreateInstance reached total limit", self.user.userCreds.getName())

    #==========================================================
    # List of enabled tasks
    #==========================================================
    tasks = [bawLogin, bawCreateInstance, bawClaimTask, bawCompleteTask, bawGetTaskData, bawSetTaskData, bawReleaseTask]

