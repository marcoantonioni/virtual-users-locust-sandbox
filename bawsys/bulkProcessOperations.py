from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
import requests
from base64 import b64encode
from bawsys import bawUtils as bawUtils 

requests.packages.urllib3.disable_warnings() 


class BpmProcessBulkOpsManager:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        self.loggedIn = False
        self.authorizationBearerToken : str = None
        self.cookieTraditional = None
        self.bpmEnvironment = bpmEnvironment
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(bpmEnvironment)
        if runningTraditional == True:
            self.cookieTraditional = bawSys._loginTraditional(self.bpmEnvironment, userName, userPassword)
            if self.cookieTraditional != None:
                self.loggedIn = True
        else:
            self.authorizationBearerToken = bawSys._loginZen(self.bpmEnvironment, userName, userPassword)
            if self.authorizationBearerToken != None:
                self.loggedIn = True

        if self.loggedIn == True:
            if runningTraditional == False:
                self._headers['Authorization'] = 'Bearer '+self.authorizationBearerToken
            else:
                self._headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

    def terminateInstances(self):
        if self.loggedIn == True:
            print("Terminating instances...")
            return self._workOnInstances(self.bpmEnvironment, "terminate")
        return None

    def deleteInstances(self, terminate: bool):
        if self.loggedIn == True:
            if terminate == True:
                print("Terminating instances...")
                self._workOnInstances(self.bpmEnvironment, "terminate")
            print("Deleting instances...")
            return self._workOnInstances(self.bpmEnvironment, "delete")
        return None

    def _workOnInstances(self, bpmEnvironment : bpmEnv.BpmEnvironment, action : str):
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        appProcessName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
        appProcessAcronym = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
        baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

        part1="action="+action+"&searchFilterScope=Both&projectFilter="+appProcessAcronym
        if action == "terminate":
            part2="&statusFilter=Active%2CFailed%2CSuspended"
        else:
            part2="&statusFilter=Completed%2CTerminated"
        queryParts = part1+part2

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        urlStartInstance = hostUrl+uriBaseRest+"/process/bulkWithFilters?"+queryParts

        response = requests.put(url=urlStartInstance, headers=self._headers, verify=False)
        if response.status_code == 200:
            jsObj = response.json()
            status = jsObj["status"]
            if status == "200":
                data = response.json()["data"]
                print("Instances elaborated", data["succeeded"])
                print("Instances failed", data["failed"])
                print("")
        else:
            print(response.status_code)
            print(response.text)                
        return None
