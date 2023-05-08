import requests, json, logging, random
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bawSys
import bawsys.bawUtils as bawUtils
import bawsys.exposedProcessManager as bpmExpProcs
import urllib

requests.packages.urllib3.disable_warnings() 

class BpmProcessInstance:
    def __init__(self, state: str, piid: str, caseFolderID: str, caseFolderServerName: str, result: str, 
                    startingDocumentServerName: str, parentCaseId: str, parentActivityId: str, workflowApplication: str,
                    caseIdentifier: str, caseTypeId: str, caseStageStatus: str, caseProcessTypeLocation: str):
      self.state = state 
      self.piid = piid
      self.caseFolderID = caseFolderID
      self.caseFolderServerName = caseFolderServerName
      self.result = result
      self.startingDocumentServerName = startingDocumentServerName
      self.parentCaseId = parentCaseId
      self.parentActivityId = parentActivityId
      self.workflowApplication = workflowApplication
      self.caseIdentifier = caseIdentifier
      self.caseTypeId = caseTypeId
      self.caseStageStatus = caseStageStatus
      self.caseProcessTypeLocation = caseProcessTypeLocation

    def getState(self):
      return self.state 

    def getPiid(self):
      return self.piid

    def getCaseFolderID(self):
      return self.caseFolderID

    def getCaseFolderServerName(self):
      return self.caseFolderServerName

    def getResult(self):
      return self.result

    def getStartingDocumentServerName(self):
      return self.startingDocumentServerName

    def getParentCaseId(self):
      return self.parentCaseId

    def getParentActivityId(self):
      return self.parentActivityId

    def getWorkflowApplication(self):
      return self.workflowApplication

    def getCaseIdentifier(self):
      return self.caseIdentifier

    def getCaseTypeId(self):
      return self.caseTypeId

    def getCaseStageStatus(self):
      return self.caseStageStatus

    def getCaseProcessTypeLocation(self):
      return self.caseProcessTypeLocation


class BpmExecProcessInstance:
    def __init__(self, executionState: str, piid: str, name: str, bpdName: str, snapshotId: str, 
                    projectId: str, dueDate: str, creationDate: str, lastModTime: str, closedDate: str):
      self.executionState = executionState 
      self.piid = piid
      self.name = name
      self.bpdName = bpdName
      self.snapshotId = snapshotId
      self.projectId = projectId
      self.dueDate = dueDate
      self.creationDate = creationDate
      self.lastModTime = lastModTime
      self.closedDate = closedDate
      self.variables = None


class BpmProcessInstanceManager:

    def __init__(self):
        self.maxInstancesPerRun = 10
        self.createdInstancesPerRun = 0
        self.loggedIn = False
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def setupMaxInstances(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        if bpmEnvironment != None:
            strMax = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_INSTANCES_MAX)
            if strMax != None:
                self.maxInstancesPerRun = int(strMax)
    
    def getmMaxInstancesPerRun(self):
      return self.maxInstancesPerRun

    def consumeAllInstances(self):
       self.createdInstancesPerRun = self.maxInstancesPerRun
       
    def consumeInstance(self):
        ok = False
        if self.createdInstancesPerRun < self.maxInstancesPerRun:
          self.createdInstancesPerRun += 1
          ok = True
        return ok

    def createInstance(self, bpmEnvironment : bpmEnv.BpmEnvironment, runningTraditional, userName, processInfo: bawSys.BpmExposedProcessInfo, payload : str, my_headers, my_cookies=None):                
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        urlStartInstance = hostUrl+processInfo.getStartUrl()+"&parts=header&params="+payload
        response = requests.post(url=urlStartInstance, headers=my_headers, cookies=my_cookies, verify=False)
        if response.status_code == 200:
            processInstance = None
            data = response.json()["data"]
            if runningTraditional == False:
                processInstance = BpmProcessInstance(data["state"], data["piid"], data["caseFolderID"], data["caseFolderServerName"], data["result"], 
                                                      data["startingDocumentServerName"], data["parentCaseId"], data["parentActivityId"], data["workflowApplication"], 
                                                      data["caseIdentifier"], data["caseTypeId"], data["caseStageStatus"], data["caseProcessTypeLocation"])
            else:
                processInstance = BpmProcessInstance(data["state"], data["piid"], data["caseFolderID"], data["caseFolderServerName"], data["result"], 
                                                      data["startingDocumentServerName"], data["parentCaseId"], data["parentActivityId"], data["workflowApplication"], 
                                                      None, None, None, None)
            return processInstance
        else:
            if response.status_code >= 300 and response.status_code != 401:
                logging.error("createInstance error, user %s, status code [%d], message [%s]", userName, response.status_code, response.text)
        return None

    def searchProcessInstances(self, bpmEnvironment : bpmEnv.BpmEnvironment, bpdName: str, status: str, dateFrom: str, dateTo: str):
        listOfInstances = None

        self.loggedIn = False
        authorizationBearerToken = None
        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(bpmEnvironment)
        if runningTraditional == True:
            cookieTraditional = bawSys._loginTraditional(bpmEnvironment, userName, userPassword)
            if cookieTraditional != None:
                self.loggedIn = True
        else:
            authorizationBearerToken = bawSys._loginZen(bpmEnvironment, userName, userPassword)
            if authorizationBearerToken != None:
                self.loggedIn = True

        if self.loggedIn == True:
            if runningTraditional == False:
                self._headers['Authorization'] = 'Bearer '+authorizationBearerToken
            else:
                self._headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

            hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            baseUri : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            appAcronym : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)

            statusFilter = ""
            if status != None and status != "":
                statusFilter = "&statusFilter="+status
            
            modifiedAfter = ""
            if dateFrom != None and dateFrom != "":
                modifiedAfter = "&modifiedAfter="+dateFrom

            modifiedBefore = ""
            if dateTo != None and dateTo != "":
                modifiedBefore = "&modifiedBefore="+dateTo

            fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/processes/search?projectFilter="+appAcronym+statusFilter+modifiedAfter+modifiedBefore
            response = requests.post(url=fullUrl, headers=self._headers, verify=False)
            if response.status_code == 200:
                jsObj = response.json()
                data = jsObj["data"]
                processes = data["processes"]
                numProcesses = len(processes)
                idx = 0
                listOfInstances = []
                while idx < numProcesses:
                    p = processes[idx]
                    closedDate = ""
                    try:
                      closedDate = p["closedDate"]
                    except KeyError:
                      pass

                    if bpdName == None or bpdName == p["bpdName"]:
                      execProc = BpmExecProcessInstance(p["executionState"], p["piid"], p["name"], p["bpdName"], p["snapshotID"], 
                                                        p["projectID"], p["dueDate"], p["creationDate"], p["lastModificationTime"], closedDate)
                      listOfInstances.append(execProc)
                    idx += 1
            else:
                if response.status_code >= 300 and response.status_code != 401:
                    logging.error("searchProcessInstances error, user %s, status code [%d], message [%s]", userName, response.status_code, response.text)

        return listOfInstances

    def _getProcessDetails(self, hostUrl, baseUri, pid):
        fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/process/"+pid+"?parts=data"
        response = requests.get(url=fullUrl, headers=self._headers, verify=False)
        if response.status_code == 200:
            jsObj = response.json()
            data = jsObj["data"]
            variables = data["variables"]
            cleanedVars = bawUtils._cleanVarData(variables)
            #print(json.dumps(cleanedVars, indent = 2))
            return cleanedVars
        return None

    def exportProcessInstancesData(self, bpmEnvironment : bpmEnv.BpmEnvironment, bpdName: str, status: str, dateFrom: str, dateTo: str):
        listOfInstances = self.searchProcessInstances(bpmEnvironment, bpdName, status, dateFrom, dateTo)
        if listOfInstances != None:
            hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            baseUri : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            numProcesses = len(listOfInstances)
            idx = 0
            while idx < numProcesses:
                if bpdName == None or bpdName == listOfInstances[idx].bpdName:                     
                    # print("export process ", listOfInstances[idx].piid, listOfInstances[idx].bpdName, listOfInstances[idx].executionState)
                    listOfInstances[idx].variables = self._getProcessDetails(hostUrl, baseUri, listOfInstances[idx].piid)                      
                idx += 1
        return listOfInstances

    def getProcessInstanceByPid(self, bpmEnvironment, pid, variables=True):
        self.loggedIn = False
        authorizationBearerToken = None
        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(bpmEnvironment)
        if runningTraditional == True:
            cookieTraditional = bawSys._loginTraditional(bpmEnvironment, userName, userPassword)
            if cookieTraditional != None:
                self.loggedIn = True
        else:
            authorizationBearerToken = bawSys._loginZen(bpmEnvironment, userName, userPassword)
            if authorizationBearerToken != None:
                self.loggedIn = True

        if self.loggedIn == True:
            if runningTraditional == False:
                self._headers['Authorization'] = 'Bearer '+authorizationBearerToken
            else:
                self._headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

            hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
            baseUri : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

            fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/process/"+pid+"?parts=header|data"
            response = requests.get(url=fullUrl, headers=self._headers, verify=False)
            if response.status_code == 200:
                jsObj = response.json()
                p = jsObj["data"]
                closedDate = ""
                try:
                  closedDate = p["closedDate"]
                except KeyError:
                  pass
                name = p["name"]
                bpdName = name.split(":")[0]

                execProc = BpmExecProcessInstance(p["executionState"], p["piid"], name, bpdName, p["snapshotID"], 
                                                  None, p["dueDate"], p["creationTime"], p["lastModificationTime"], closedDate)
                if variables:
                    execProc.variables = self._getProcessDetails(hostUrl, baseUri, pid)    
                return execProc
            else:
                if response.status_code >= 300 and response.status_code != 401:
                    logging.error("getProcessInstanceByPid error, user %s, status code [%d], message [%s]", userName, response.status_code, response.text)
        return None

    def exportProcessInstancesDataByPid(self, bpmEnvironment : bpmEnv.BpmEnvironment, listOfPids):
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
        listOfInstances = []
        idx = 0
        for pid in listOfPids:      
            procId = self.getProcessInstanceByPid(bpmEnvironment, pid)
            if procId != None:      
                listOfInstances.append( procId )
            else:
                logging.error("Process id [%s] not found", pid)          
        return listOfInstances

    @staticmethod
    def _createProcessInstancesBatch(bpmEnvironment : bpmEnv.BpmEnvironment, 
                                      bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager,
                                      bpmProcessInstanceManager, 
                                      bpmDynamicModule,
                                      maxInstances : int, isLog=True):
      listOfInstances = []
      authorizationBearerToken = bpmExposedProcessManager.LoadProcessInstancesInfos(bpmEnvironment)

      userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
      userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
      runningTraditional = bawSys._isBawTraditional(bpmEnvironment)

      _headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
      if runningTraditional == False:
          _headers['Authorization'] = 'Bearer '+authorizationBearerToken
      else:
          _headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

      processInfoKeys = bpmExposedProcessManager.getKeys()
      totalKeys = len(processInfoKeys)

      count = 0
      while count < maxInstances:
          rndIdx : int = random.randint(0, (totalKeys-1))
          key = processInfoKeys[rndIdx]
          processName = key.split("/")[0]
          processInfo = bpmExposedProcessManager.getProcessInfos(key)  
          jsonPayloadInfos = bpmDynamicModule.buildPayloadForSubject("Start-"+processName, None, count)
          jsonPayload = jsonPayloadInfos["jsonObject"]
          strPayload = json.dumps(jsonPayload)
          processInstanceInfo = bpmProcessInstanceManager.createInstance(bpmEnvironment, runningTraditional, userName, processInfo, strPayload, _headers)
          if processInstanceInfo != None:
              listOfInstances.append(processInstanceInfo)
              if isLog:
                print("Created process "+processName+" instance id["+processInstanceInfo.getPiid()+"], state["+processInstanceInfo.getState()+"]")
          count += 1
      return listOfInstances
