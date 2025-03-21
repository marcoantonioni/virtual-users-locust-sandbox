"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import requests, json, logging, random, sys
import bawsys.bawEnvironment as bpmEnv
import bawsys.bawSystem as bpmSys
import bawsys.bawUtils as bawUtils
from json import JSONDecodeError

requests.packages.urllib3.disable_warnings() 

class BpmExposedProcessManager:
    exposedProcesses = dict()

    def __init__(self):
        self.exposedProcesses = dict()
        self.appName = None
        self.appAcronym = None
        self.appId = None
        self.bpdId = None
        self.snapshotName = None
        self.tip = False
        self.appProcessNames = None
      
    def addProcessInfos(self, key: str, processInfo: bpmSys.BpmExposedProcessInfo):
        self.exposedProcesses[key] = processInfo  

    def hasExposedProcesses(self):
        return len(self.exposedProcesses) > 0

    def removeProcessInfos(self, key: str):
        self.exposedProcesses.pop(key)

    def getProcessInfos(self, key: str):
        processInfo = None
        try:
          processInfo = self.exposedProcesses[key]
        except:
          pass
        return processInfo

    def getKeys(self):
        keysList = []
        for key in self.exposedProcesses:
            keysList.append(key)
        return keysList
    
    def getAppName(self):
        return self.appName
    
    def getAppAcronym(self):
        return self.appAcronym
    
    def getAppId(self):
        return self.appId

    def getBpdId(self):
        return self.bpdId

    def getSnapshotName(self):
        return self.snapshotName
        
    def isTip(self):
        return self.tip
    
    def getAppProcessNames(self):
        return self.appProcessNames
    
    def nextRandomProcessInfos(self):
        processInfo = None
        processInfoKeys = self.getKeys()
        totalKeys = len(processInfoKeys)
        if totalKeys >= 1:
            rndIdx : int = random.randint(0, (totalKeys-1))
            key = processInfoKeys[rndIdx]
            processInfo = self.getProcessInfos(key)  
        return processInfo 

    def LoadProcessInstancesInfos(self, bpmEnvironment : bpmEnv.BpmEnvironment, environment):
        hostUrl = bawUtils.removeSlash(bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
        token = None

        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        if bpmSys._isBawTraditional(bpmEnvironment):
            token = bpmSys._loginTraditional(bpmEnvironment, userName, userPassword) 
        else:
            token = bpmSys._loginZen(bpmEnvironment, userName, userPassword)
        if token != None:
            # 20240818
            federatedDeployment = False
            if bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_DEPLOYMENT_MODE) == bpmEnvironment.getValue(bpmEnv.BpmEnvironment.valBAW_DEPLOYMENT_MODE_PAK_FEDERATED):
                federatedDeployment = True

            response = None
            baseUri = bawUtils.removeSlash(bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)

            # 20240818
            if federatedDeployment == True:
                urlExposed = hostUrl+"/pfs/rest/bpm/federated/v1/launchableEntities?avoidBasicAuthChallenge=true"
            else:
                urlExposed = hostUrl+baseUri+"/rest/bpm/wle/v1/exposed/process?excludeProcessStartUrl=false"

            # print("==>> LoadProcessInstancesInfos %s", urlExposed)

            my_headers = None
            if bpmSys._isBawTraditional(bpmEnvironment):
                my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                response = requests.get(url=urlExposed, headers=my_headers, cookies=token, verify=False)
            else:
                my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+token }
                response = requests.get(url=urlExposed, headers=my_headers, verify=False)
            if response.status_code == 200:
                if federatedDeployment == True:
                    data = response.json()
                    exposedItemsList = data["items"]
                else:
                    data = response.json()["data"]
                    exposedItemsList = data["exposedItemsList"]

                # print(json.dumps(data, indent=2))
                # print(json.dumps(exposedItemsList, indent=2))

                self.appName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
                self.appAcronym = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
                appSnapshotName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
                strUseTip = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP)
                processNames = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_NAMES)
                self.appProcessNames = processNames.split(",")
                useTip = False
                if strUseTip != None:
                    if strUseTip.lower() == "true":
                        useTip = True
                else:
                    logging.error("Error, invalid 'tip' value, BAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP must be one of 'true' or 'false'. Quitting now")
                    if environment != None:
                        environment.runner.quit()

                if appSnapshotName == None or appSnapshotName == "":
                    appSnapshotName = ""
                    useTip = True
                self.snapshotName = appSnapshotName
                self.tip = useTip

                listOfProcessInfos = []
                for expIt in exposedItemsList:
                    try:
                        snapOk = False

                        # print(">>>>>>>>>>>> ", expIt["processAppName"], expIt["processAppAcronym"], expIt["tip"], useTip, "appSnapshotName="+appSnapshotName)

                        if self.appName == expIt["processAppName"] and self.appAcronym == expIt["processAppAcronym"]: 

                            # print(json.dumps(expIt, indent=2))

                            if appSnapshotName == "" and useTip == True and expIt["tip"] == True:                                
                                snapOk = True
                            else:
                                if appSnapshotName == expIt["snapshotName"]:
                                    # if useTip: 
                                    #    if expIt["tip"].lower() == "true":
                                    snapOk = True
                            # print("==== snapOk: ", snapOk)
                            if snapOk == True:
                                if self.appId == None:
                                    self.appId = expIt["processAppID"] 
                                processName = expIt["display"]                   
                                bpdId = expIt["itemID"]     
                                startUrl = expIt["startURL"]
                                for pn in self.appProcessNames:
                                    if pn == processName:                                                                                                        
                                        listOfProcessInfos.append( bpmSys.BpmExposedProcessInfo(self.appName, self.appAcronym, self.snapshotName, self.tip, processName, self.appId, bpdId, startUrl) )
                                        logging.info("Added process name [%s] from app[%s, %s, %s] appId [%s] itemId [%s]", processName, self.appName, self.appAcronym, self.snapshotName, self.appId, expIt["itemID"])                                     
                    except KeyError:
                        pass

                if len(listOfProcessInfos) == 0:
                    logging.error("Error looking for application [%s] [%s], configured snapshot '%s' not present or not activated or not available as tip. Use empty value in BAW_PROCESS_APPLICATION_SNAPSHOT_NAME to run against the Tip. Or BAW_POWER_USER_NAME has not sufficient grants to eccess exposed processes, quitting now.", self.appName, self.appAcronym, appSnapshotName)
                    if environment != None:
                        environment.runner.quit()

                for appProcInfo in listOfProcessInfos:
                    self.addProcessInfos(appProcInfo.getKey(), appProcInfo)
            else:
                contextName = "LoadProcessInstancesInfos"
                js = {}
                try:
                    js = response.json()
                except:
                    logging.error("%s status code: %s, empty/not-valid json content", contextName, response.status_code)
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("%s status code: %s", contextName, response.status_code)
                if response.status_code >= 300:
                    try:
                        data = js["Data"]
                        bpmErrorMessage = data["errorMessage"]
                        logging.error("%s error, message [%s]", contextName, bpmErrorMessage)
                    except JSONDecodeError:
                        logging.error("%s error, response could not be decoded as JSON", contextName)
                        self.response.failure("Response could not be decoded as JSON")
                    except KeyError:
                        logging.error("%s error, response did not contain expected key 'Data', 'errorMessage'", contextName)
                        self.response.failure("Response did not contain expected key 'Data', 'errorMessage'")
        else:
            logging.error("Login failed for user [%s], terminating...", userName)
            environment.runner.quit()
            
        return token
    
    def loadExposedItemsForUser(self, bpmEnvironment : bpmEnv.BpmEnvironment, processInfo: bpmSys.BpmExposedProcessInfo, user):
        forMe = False
        response = None
        hostUrl = bawUtils.removeSlash(bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
        baseUri = bawUtils.removeSlash(bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)
        urlExposed = hostUrl+baseUri+"/rest/bpm/wle/v1/exposed/process?excludeProcessStartUrl=false"

        my_headers = None
        if bpmSys._isBawTraditional(bpmEnvironment):
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            response = requests.get(url=urlExposed, headers=my_headers, cookies=user.cookieTraditional, verify=False)
        else:
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+user.authorizationBearerToken }
            response = requests.get(url=urlExposed, headers=my_headers, verify=False)
        
        if response.status_code == 200:
            data = response.json()["data"]
            
            # print(json.dumps(data, indent=2))
            
            exposedItemsList = data["exposedItemsList"]
            if exposedItemsList != None:

                for expItem in exposedItemsList:

                    # type: process, ???

                    # print("expItem", json.dumps(expItem,indent=2))

                    snapName = ""
                    appName = ""
                    snapName = ""
                    acrName = ""
                    try:
                        acrName = expItem["processAppAcronym"]
                        if acrName == None:
                            acrName = ""
                    except:
                        pass
                    try:
                        appName = expItem["processAppName"]
                        if appName == None:
                            appName = ""
                    except:
                        pass
                    try:
                        snapName = expItem["snapshotName"]
                        if snapName == None:
                            snapName = ""
                    except:
                        pass
                    procName = expItem["display"]
                    tipItem = expItem["tip"]

                    # forza snapshot se configurata tip
                    if processInfo.isTip() and tipItem:
                        snapName = processInfo.getSnapshotName()
                    if appName == processInfo.getAppName() and acrName == processInfo.getAppAcronym() and procName == processInfo.getAppProcessName() and snapName == processInfo.getSnapshotName():
                        forMe = True
                        break

        else:
            print(response.status_code, response.text)

        return forMe 