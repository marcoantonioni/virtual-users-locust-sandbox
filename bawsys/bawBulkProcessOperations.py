"""
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from bawsys import bawEnvironment as bpmEnv
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
