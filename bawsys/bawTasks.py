"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging, json, sys, random, time
from datetime import datetime
from locust import task, tag, SequentialTaskSet
import bawsys.bawProcessInstanceManager as bawPIM
from bawsys.bawProcessInstanceManager import BpmProcessInstance as bpmPI
from bawsys import bawEnvironment as bpmEnv
from bawsys import bawSystem as bawSys 
from bawsys import bawRestResponseManager as responseMgr 
from bawsys import bawUtils as bawUtils 
from bawsys import bawUniTestScenarioManager as bawTSM
from requests.cookies import cookiejar_from_dict

class SequenceOfBpmTasks(SequentialTaskSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # unit test scenario
        self.isUnitTest = False

    #==========================================================
    # Supporting functions
    #==========================================================

    def forceLogin(self):
        self.user.loggedIn = False
        self.user.cookieTraditional = None
        self.user.authorizationBearerToken = None
        self.bawLogin()

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

    def _prepareHeaders(self, forceBasicAuth=False):
        _headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if self.user.runningTraditional == False:
            _headers['Authorization'] = 'Bearer '+self.user.authorizationBearerToken
        else:
            if forceBasicAuth == True:
                _headers['Authorization'] = bawUtils._basicAuthHeader(self.user.userCreds.getName(), self.user.userCreds.getPassword())
            else:
                if self.user.cookieTraditional != None:
                    cookiejar_from_dict(self.user.cookieTraditional.get_dict(), self.client.cookiejar)
        return _headers

    def _buildTaskUrl(self, bpmTask : bawSys.BpmTask):
        fullUrl = ""
        if bpmTask.isFederatedSystem():
            fullUrl = bpmTask.getFederatedSystem().getRestUrlPrefix()+"/v1/task/"+bpmTask.getId()
        else:
            hostUrl : str = bawUtils.removeSlash(self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
            baseUri : str = bawUtils.removeSlash(self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)
            fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/task/"+bpmTask.getId()
        return fullUrl

    def _buildTaskList(self, tasksCount, tasksList, interaction):

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("_buildTaskList - tasksCount %s, taskListLen %d", tasksCount, len(tasksList))

        # print(json.dumps(tasksList,indent=2))

        isClaiming = False
        if interaction == "available":
            isClaiming = True

        epm = self.user.getExposedProcessManager()
        snapName = epm.getSnapshotName()    
        appAcronym = epm.getAppAcronym()

        configuredSnapName = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
        strTip = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP)
        useTip = False
        if strTip.lower() == "true":
            useTip = True
        if configuredSnapName == None or configuredSnapName == "":
            configuredSnapName = snapName
            useTip = True

        #print("===> ", snapName, configuredSnapName, appAcronym, useTip, len(tasksList))

        bpmTaksItems = []
        while len(tasksList) > 0:            
            bpmTask : bawSys.BpmTask = bawSys.BpmTask( tasksList.pop() )

            if snapName == configuredSnapName:
                selectTask = False
                if useTip == True:
                    selectTask = True
                else:
                    if bpmTask.getSnapshotName() == None and useTip == True:
                        selectTask = True
                    else:
                        if bpmTask.getSnapshotName() != None and bpmTask.getSnapshotName() == configuredSnapName:
                            selectTask = True

                # print("==========> taskSubject", bpmTask.getSubject(), bpmTask.getProcessName(), selectTask)
                
                if selectTask == True:
                    # inserisce in lista se task di processo configurato
                    listOfProcessNames = epm.getAppProcessNames()       
                    
                    # print("===========> listOfProcessNames: ", len(listOfProcessNames))                                 
                    
                    for procName in listOfProcessNames:
                        # print("====================> procName: ", procName)

                        # if procName == bpmTask.getProcessName():
                        if procName.find(bpmTask.getProcessName()) != -1:
                            # print("====================> procName OK: ", procName)

                            if self.user.isSubjectForUser(bpmTask.getSubject()) == True:
                                # print("===============> OK subject for user ")
                                if (bpmTask.getRole() != None and isClaiming == True) or (bpmTask.getRole() == None and isClaiming == False):  
                                    # print("====================> append task: ", bpmTask.getSubject(), bpmTask.getProcessName())                                  
                                    bpmTaksItems.append(bpmTask)
        
        return bawSys.BpmTaskList(len(bpmTaksItems), bpmTaksItems)

    def _listTasks(self, interaction, size):
        if self.user.loggedIn == True:
            uriBaseTaskList = ""
            taskListFederated = False
            hostUrl : str = bawUtils.removeSlash(self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
            processAppName = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
            # processAppAcronym = self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
            
            # query task list
            offset = "0"
            constParams : str = "interaction=claimed_and_available&calcStats=false&includeAllBusinessData=false"

            my_headers = self._prepareHeaders()
            # nameType = None

            baseUri = bawUtils.removeSlash(self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)
            if baseUri == None:
                baseUri = ""
            uriBaseTaskList = baseUri+"/rest/bpm/wle/v1/tasks"

            if self.user.runningTraditional == False:
                if self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_DEPLOYMENT_MODE) == self.user.getEnvValue(bpmEnv.BpmEnvironment.valBAW_DEPLOYMENT_MODE_PAK_FEDERATED):
                    taskListFederated = True
                    uriBaseTaskList = "/pfs/rest/bpm/federated/v1/tasks"

                # 20240817
                # nameType = processAppAcronym
                #nameType = processAppName
            #else:
            #    baseUri = bawUtils.removeSlash(self.user.getEnvValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)
            #    if baseUri == None:
            #        baseUri = ""
            #    uriBaseTaskList = baseUri+"/rest/bpm/wle/v1/tasks"
            #    #nameType = processAppName
            
            fullUrl = hostUrl+uriBaseTaskList+"?"+constParams+"&offset="+offset+"&size=25&processAppName="+processAppName

            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("==>> _listTasks fullURL: %s", fullUrl)

            with self.client.get(url=fullUrl, headers=my_headers, catch_response=True) as response:

                restResponseManager: responseMgr.RestResponseManager = responseMgr.RestResponseManager("_listTasks", response, self.user.userCreds.getName(), None, [401, 409])
                if restResponseManager.getStatusCode() == 200:

                    # print(json.dumps(response.json(),indent=2))

                    _taskList = None
                    size = 0
                    items = None
                    if self.user.runningTraditional == False:

                        # 20240817
                        # size = restResponseManager.getObject("size")
                        # items = restResponseManager.getObject("items")

                        data = restResponseManager.getObject("data")
                        size = data["size"]
                        try:
                            items = data["items"]
                        except KeyError:
                            pass

                        # print("user: %s, size: %d", self.user.userCreds.getName(), size)

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
                else:
                    if restResponseManager.getStatusCode() == 401:
                        self.forceLogin()
            return None

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
                else:
                    if restResponseManager.getStatusCode() == 401:
                        self.forceLogin()
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
                else:
                    if restResponseManager.getStatusCode() == 401:
                        self.forceLogin()
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
                else:
                    if restResponseManager.getStatusCode() == 401:
                        self.forceLogin()
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
                else:
                    if restResponseManager.getStatusCode() == 401:
                        self.forceLogin()
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
                    else:
                        if restResponseManager.getStatusCode() == 401:
                            self.forceLogin()
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
                else:
                    if restResponseManager.getStatusCode() == 401:
                        self.forceLogin()
        return False


    #==========================================================
    # Task functions
    #==========================================================
    
    @task
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
                        think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                        time.sleep( think )
                    else:
                        logging.error("User[%s] - bawLogin - failed login", userName)

    @task
    def bawRefreshListTask(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_REFRESH_TASK_LIST ):
                taskList : bawSys.BpmTaskList = self._listTasks("claimed_and_available", 25)
                if taskList != None:
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("User[%s] - bawRefreshListTask num TASKS [%d]", self.user.userCreds.getName(),taskList.getCount())
                else:
                    self.nothingToDo("bawRefreshListTask task in list")
                think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                time.sleep( think )
        else:
            self.forceLogin()

    @task
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
                                logging.info("User[%s] - bawClaimTask - claimed task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                if self._taskGetDetails(bpmTask) == True:
                                    logging.debug("bawClaimTask TASK [%s] DETAIL AFTER CLAIM actions[%s] variables[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions(), bpmTask.getVariableNames())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawClaimTask TASK [%s] CONFLICT, cannot claim task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())
                else:
                    self.nothingToDo("bawClaimTask no task to claim")
                think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                time.sleep( think )
        else:
            self.forceLogin()

    @task
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
                                logging.info("User[%s] - bawCompleteTask working on task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
                                if self._taskComplete(bpmTask, payload) == True:
                                    self.user.idleCounter = 0
                                    logging.info("User[%s] - bawCompleteTask - completed task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
                            else:
                                if logging.getLogger().isEnabledFor(logging.DEBUG):
                                    logging.debug("User[%s] - bawCompleteTask TASK [%s] ERROR, cannot _taskGetData, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawCompleteTask TASK [%s] CONFLICT, cannot complete already claimed task, actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())
                else:
                    self.nothingToDo("bawCompleteTask no task to complete")
        else:
            self.forceLogin()

    @task
    def bawGetTaskData(self):
        if self.user.loggedIn == True:
            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_GETDATA ):
                taskList = self._listTasks("claimed", 25)
                if taskList != None and taskList.getCount() > 0:    
                    bpmTask : bawSys.BpmTask = taskList.getPreparedTaskRandom()
                    if self._taskGetData(bpmTask) == True:
                        self.user.idleCounter = 0
                        logging.info("User[%s] - bawGetTaskData - read data from task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
                    if logging.getLogger().isEnabledFor(logging.DEBUG):
                        logging.debug("User[%s] - bawGetTaskData TASK [%s] CLEANED TASK DATA %s", self.user.userCreds.getName(), bpmTask.getId(), json.dumps(bpmTask.getTaskData(), indent = 2))
                else:
                    self.nothingToDo("bawGetTaskData no task to set data")
                think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                time.sleep( think )
        else:
            self.forceLogin()

    @task
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
                                logging.info("User[%s] - bawSetTaskData working on task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
                                if self._taskSetData(bpmTask, payload) == True:
                                    self.user.idleCounter = 0
                                    logging.info("User[%s] - bawSetTaskData - set data and postponed on task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
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
        else:
            self.forceLogin()

    @task
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
                                logging.info("User[%s] - bawReleaseTask - released task[%s] subject[%s]", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getSubject())
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] RELEASED ", self.user.userCreds.getName(), bpmTask.getId())
                        else:
                            if logging.getLogger().isEnabledFor(logging.DEBUG):
                                logging.debug("User[%s] - bawReleaseTask TASK [%s] HAS NO ACTION_CANCELCLAIM, available actions %s", self.user.userCreds.getName(), bpmTask.getId(), bpmTask.getActions())
                else:
                    self.nothingToDo("bawReleaseTask no task to release")
                think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
                time.sleep( think )
        else:
            self.forceLogin()

    @task
    def bawCreateInstance(self):
        if self.isUnitTest == False:
            if self.user.loggedIn == True:
                if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS ): 
                    pim = self.user.getPIM()
                    if pim.consumeInstance() == True:
                        pem = self.user.getEPM()
                        processInfo: bawSys.BpmExposedProcessInfo = pem.nextRandomProcessInfos()
                        if processInfo != None:
                            if pem.loadExposedItemsForUser(self.user.getEnvironment(), processInfo, self.user):
                                processName = processInfo.getAppProcessName()
                                jsonPayloadInfos = self._buildPayload("Start-"+processName)
                                jsonPayload = bawUtils._extractPayloadOptionalThinkTime(jsonPayloadInfos, self.user, True)
                                strPayload = json.dumps(jsonPayload)
                                my_headers = self._prepareHeaders()
                                processInstanceInfo : bpmPI = pim.createInstance(self.user.getEnvironment(), self.user.runningTraditional, self.user.userCreds.getName(), processInfo, strPayload, my_headers, self.user.cookieTraditional)
                                if processInstanceInfo != None:
                                    logging.info("User[%s] - bawCreateInstance - process name[%s] - process id[%s], state[%s]", self.user.userCreds.getName(), processName, processInstanceInfo.getPiid(), processInstanceInfo.getState())
                        else:
                            logging.error("User[%s] - bawCreateInstance no process info available", self.user.userCreds.getName())
                            # da rivedere gestione errore creazione istanza
                            self.forceLogin()
                    else:
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug("User[%s] - bawCreateInstance reached total limit", self.user.userCreds.getName())

            else:
                self.forceLogin()

    #==========================================================
    # List of enabled tasks
    #==========================================================
    tasks = [bawLogin, 
                bawCreateInstance, 
                bawRefreshListTask, 
                bawClaimTask, 
                bawGetTaskData, 
                bawSetTaskData, 
                bawCompleteTask, 
                bawReleaseTask]

class UnitTestScenario(SequenceOfBpmTasks):
    tsMgr = None
    instanceCreated = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.isUnitTest = True
        self.instanceCreated = False
        if UnitTestScenario.tsMgr == None:
            UnitTestScenario.tsMgr : bawTSM.TestScenarioManager = bawTSM.TestScenarioManager(self.user.getEnvironment())
    
    @task
    def bawCreateScenarioInstances(self):
        if UnitTestScenario.instanceCreated == False:
            UnitTestScenario.instanceCreated = True            
            pim = self.user.getPIM()
            maxInstances = pim.getmMaxInstancesPerRun()
            pim.consumeAllInstances()
            userName = self.user.getEnvironment().getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)

            if self.isActionEnabled(bpmEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS ):                              
                logging.info("User[%s] - bawCreateScenarioInstances - creating [%d] instances", userName, maxInstances)
            else:
                maxInstances = 0
                logging.info("User[%s] - bawCreateScenarioInstances - no instances will be created, action 'BAW_ACTION_CREATEPROCESS' is disabled.", userName)

            listOfInstances = pim._createProcessInstancesBatch(self.user.getEnvironment(), self.user.getExposedProcessManager(), pim, 
                                                                self.user.getDynamicModule(), maxInstances, isLog=False)
            for p in listOfInstances:
                UnitTestScenario.tsMgr.addInstance(p)
        return
            
    #==========================================================
    # List of enabled tasks
    #==========================================================
    tasks = [bawCreateScenarioInstances] + SequenceOfBpmTasks.tasks
