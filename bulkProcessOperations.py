from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
#from bawsys import loadEnvironment
#from bawsys import exposedProcessManager
import urllib, requests, json

requests.packages.urllib3.disable_warnings() 


class BpmProcessBulkOpsManager:

    def __init__(self):
      self.cp4ba_token : str = None

    def terminateInstances(self):
       pass

    def deleteInstances(self):
       pass


    def terminateInstances(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)

        if self.cp4ba_token == None:
            self.cp4ba_token = bawSys._loginZen(bpmEnvironment, iamUrl, hostUrl)
        if self.cp4ba_token != None:
            print("Terminating instances...")
            return self._workOnInstances(bpmEnvironment, "terminate")
        return None

    def deleteInstances(self, bpmEnvironment : bpmEnv.BpmEnvironment, terminate: bool):
        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)

        if self.cp4ba_token == None:
            self.cp4ba_token = bawSys._loginZen(bpmEnvironment, iamUrl, hostUrl)
        if self.cp4ba_token != None:
            if terminate == True:
                print("Terminating instances...")
                self._workOnInstances(bpmEnvironment, "terminate")
            print("Deleting instances...")
            return self._workOnInstances(bpmEnvironment, "delete")
        return None

    def _workOnInstances(self, bpmEnvironment : bpmEnv.BpmEnvironment, action : str):
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        appProcessName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
        appProcessAcronym = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
        baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

        authValue : str = "Bearer "+self.cp4ba_token
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        part1="action="+action+"&searchFilterScope=Both&projectFilter="+appProcessAcronym
        if action == "terminate":
            part2="&statusFilter=Active%2CFailed%2CSuspended"
        else:
            part2="&statusFilter=Completed"
        queryParts = part1+part2

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        urlStartInstance = hostUrl+uriBaseRest+"/process/bulkWithFilters?"+queryParts

        response = requests.put(url=urlStartInstance, headers=my_headers, verify=False)
        if response.status_code == 200:
            status = response.json()["status"]
            if status == "200":
                data = response.json()["data"]
                print("Instances elaborated", data["succeeded"])
                print("Instances failed", data["failed"])
                print("")
        else:
            print(response.status_code)
            print(response.text)                
        return None
