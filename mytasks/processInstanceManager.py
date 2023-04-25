import requests, json, logging
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

    def createInstance(self, bpmEnvironment : bpmEnv.BpmEnvironment, runningTraditional, userName, processInfo: bpmSys.BpmExposedProcessInfo, payload : str, my_headers):                
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        urlStartInstance = hostUrl+processInfo.getStartUrl()+"&parts=header&params="+payload
        response = requests.post(url=urlStartInstance, headers=my_headers, verify=False)
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
            logging.error("createInstance error, user %s, status code [%d], message [%s]", userName, response.status_code, response.text)
        return None

