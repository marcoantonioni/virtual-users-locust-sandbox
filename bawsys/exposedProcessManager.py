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
                # authValue : str = "Bearer "+token
                
                #???? provare uso cookies con valore None
                # my_cookies = None
                # cookies=my_cookies, 
                my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+token }
                response = requests.get(url=urlExposed, headers=my_headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()["data"]

                # print(json.dumps(data, indent=2))

                exposedItemsList = data["exposedItemsList"]
                self.appName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
                self.appAcronym = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
                appSnapshotName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
                processNames = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_NAMES)
                self.appProcessNames = processNames.split(",")
                if appSnapshotName == None:
                    appSnapshotName = ""
                listOfProcessInfos = []
                for expIt in exposedItemsList:
                    try:
                        snapOk = False
                        if self.appName == expIt["processAppName"] and self.appAcronym == expIt["processAppAcronym"]: 
                            if appSnapshotName == "" and expIt["tip"] == True:                                
                                snapOk = True
                            else:
                                if appSnapshotName == expIt["snapshotName"]:
                                    snapOk = True
                            if snapOk == True:
                                if self.appId == None:
                                    self.appId = expIt["processAppID"] 
                                    self.bpdId = expIt["itemID"]
                                    self.snapshotName = expIt["snapshotName"]
                                    self.tip = expIt["tip"]
                                processName = expIt["display"]                        
                                for pn in self.appProcessNames:
                                    if pn == processName:                        
                                        listOfProcessInfos.append( bpmSys.BpmExposedProcessInfo(self.appName, self.appAcronym, self.snapshotName, self.tip, processName, expIt["processAppID"], expIt["itemID"], expIt["startURL"]) )
                    except KeyError:
                        pass


                if len(listOfProcessInfos) == 0:
                    logging.error("Error, configured snapshot '%s' not present or not activated. Use blank value in BAW_PROCESS_APPLICATION_SNAPSHOT_NAME to run against the Tip", appSnapshotName)
                    sys.exit()

                for appProcInfo in listOfProcessInfos:
                    key = appProcInfo.getAppProcessName()+"/"+appProcInfo.getAppName()+"/"+appProcInfo.getAppAcronym()+"/"+appProcInfo.getSnapshotName()
                    self.addProcessInfos(key, appProcInfo)
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