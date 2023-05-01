import requests, json, logging, random, sys
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bpmSys
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

    def LoadProcessInstancesInfos(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        token = None

        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        if bpmSys._isBawTraditional(bpmEnvironment):
            token = bpmSys._loginTraditional(bpmEnvironment, userName, userPassword) 
        else:
            token = bpmSys._loginZen(bpmEnvironment, userName, userPassword)
        
        if token != None:
            response = None
            baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            urlExposed = hostUrl+baseUri+"/rest/bpm/wle/v1/exposed/process?excludeProcessStartUrl=false"

            my_headers = None
            if bpmSys._isBawTraditional(bpmEnvironment):
                my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                response = requests.get(url=urlExposed, headers=my_headers, cookies=token, verify=False)
            else:
                my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+token }
                response = requests.get(url=urlExposed, headers=my_headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()["data"]

                # print(json.dumps(data, indent=2))

                exposedItemsList = data["exposedItemsList"]
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
                    logging.error("Error, invalid 'tip' value, BAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP must be one of 'true' or 'false'")
                    sys.exit()
                if appSnapshotName == None or appSnapshotName == "":
                    appSnapshotName = ""
                    useTip = True
                self.snapshotName = appSnapshotName
                self.tip = useTip

                listOfProcessInfos = []
                for expIt in exposedItemsList:
                    try:
                        snapOk = False

                        # print(expIt["processAppName"], expIt["processAppAcronym"], expIt["tip"], useTip)

                        if self.appName == expIt["processAppName"] and self.appAcronym == expIt["processAppAcronym"]: 

                            # print(json.dumps(expIt, indent=2))

                            if appSnapshotName == "" and useTip == True and expIt["tip"] == True:                                
                                snapOk = True
                            else:
                                if appSnapshotName == expIt["snapshotName"] and useTip == expIt["tip"]:
                                    snapOk = True
                            if snapOk == True:
                                if self.appId == None:
                                    self.appId = expIt["processAppID"] 
                                processName = expIt["display"]                   
                                bpdId = expIt["itemID"]     
                                startUrl = expIt["startURL"]
                                for pn in self.appProcessNames:
                                    if pn == processName:                                                                                                        
                                        # print(self.appName, self.appAcronym, self.snapshotName, self.tip, processName, self.appId, expIt["itemID"])
                                        listOfProcessInfos.append( bpmSys.BpmExposedProcessInfo(self.appName, self.appAcronym, self.snapshotName, self.tip, processName, self.appId, bpdId, startUrl) )
                    except KeyError:
                        pass

                if len(listOfProcessInfos) == 0:
                    logging.error("Error looking for application [%s] [%s], configured snapshot '%s' not present or not activated or not available as tip. Use empty value in BAW_PROCESS_APPLICATION_SNAPSHOT_NAME to run against the Tip. Or BAW_POWER_USER_NAME has not sufficient grants to eccess exposed processes", self.appName, self.appAcronym, appSnapshotName)
                    sys.exit()

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
        return token
    
    def loadExposedItemsForUser(self, bpmEnvironment : bpmEnv.BpmEnvironment, processInfo: bpmSys.BpmExposedProcessInfo, user):
        forMe = False
        response = None
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
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
            for expItem in exposedItemsList:
                snapName = ""
                appName = expItem["processAppName"] 
                acrName = expItem["processAppAcronym"]
                procName = expItem["display"]
                tipItem = expItem["tip"]
                snapName = ""
                try:
                    snapName = expItem["snapshotName"]
                    if snapName == None:
                        snapName = ""
                except:
                    pass

                #if appName == "VirtualUsersSandbox":
                #    print(json.dumps(expItem, indent=2))
                #    print("item ", appName,acrName,procName,snapName,tipItem)
                #    print("pinfo", processInfo.getAppName(),processInfo.getAppAcronym(),processInfo.getAppProcessName(),processInfo.getSnapshotName(),processInfo.isTip())
                #    print()

                # forza snapshot se configurata tip
                if processInfo.isTip() and tipItem:
                    snapName = processInfo.getSnapshotName()
                if appName == processInfo.getAppName() and acrName == processInfo.getAppAcronym() and procName == processInfo.getAppProcessName() and snapName == processInfo.getSnapshotName():
                    forMe = True
                    break

        else:
            print(response.status_code, response.text)

        return forMe 