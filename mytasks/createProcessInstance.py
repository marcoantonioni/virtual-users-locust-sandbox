import requests, json
import mytasks.loadEnvironment as bpmEnv
import mytasks.bawSystem as bpmSys
import urllib

requests.packages.urllib3.disable_warnings() 


"""
{
  "state": "STATE_RUNNING",
  "piid": "6921",
  "caseFolderID": "2126.fd5c1446-23c4-4fb2-8245-f23e50805e81",
  "caseFolderServerName": "IBM_BPM_ManagedStore",
  "result": null,
  "startingDocumentServerName": null,
  "parentCaseId": null,
  "parentActivityId": null,
  "workflowApplication": null,
  "caseIdentifier": null,
  "caseTypeId": null,
  "caseStageStatus": null,
  "caseProcessTypeLocation": null,
"""


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
            return data
        else:
            print(response.status_code)
            print(response.text)                
        return None
    

