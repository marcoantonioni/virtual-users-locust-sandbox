import requests, json
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bpmSys
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


class BpmProcessInstanceManager:

    def __init__(self):
      self.cp4ba_token : str = None

    def createInstance(self, bpmEnvironment : bpmEnv.BpmEnvironment, processInfo: bpmSys.BpmExposedProcessInfo, payload : str, token: str):
        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)

        if self.cp4ba_token == None:
            if token != None:
                self.cp4ba_token = token
            else:
                self.cp4ba_token = bpmSys._loginZen(bpmEnvironment, iamUrl, hostUrl)
        if self.cp4ba_token != None:
            return self._createInstance(bpmEnvironment, processInfo, payload)
        return None

    def _createInstance(self, bpmEnvironment : bpmEnv.BpmEnvironment, processInfo: bpmSys.BpmExposedProcessInfo, payload : str):
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        authValue : str = "Bearer "+self.cp4ba_token
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
        urlStartInstance = hostUrl+processInfo.getStartUrl()+"&parts=header&params="+payload
        response = requests.post(url=urlStartInstance, headers=my_headers, verify=False)
        if response.status_code == 200:
            data = response.json()["data"]

            #print(json.dumps(data, indent = 2))

            # salvare dati risposta nuovo oggetto
            return BpmProcessInstance(data["state"], data["piid"], data["caseFolderID"], data["caseFolderServerName"], data["result"], 
                                        data["startingDocumentServerName"], data["parentCaseId"], data["parentActivityId"], data["workflowApplication"], data["caseIdentifier"], 
                                        data["caseTypeId"], data["caseStageStatus"], data["caseProcessTypeLocation"])
        else:
            print(response.status_code)
            print(response.text)                
        return None
    

