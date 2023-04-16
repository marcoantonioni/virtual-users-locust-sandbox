import requests, json, logging
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bpmSys
from json import JSONDecodeError

requests.packages.urllib3.disable_warnings() 

class BpmExposedProcessManager:
    exposedProcesses = dict()

    def __init__(self):
      self.exposedProcesses = dict()
      self.appId = None
      self.bpdId = None

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
    
    def getAppId(self):
        return self.appId

    def getBpdId(self):
        return self.bpdId

    def LoadProcessInstancesInfos(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        cp4ba_token : str = bpmSys._loginZen(bpmEnvironment, iamUrl, hostUrl)
        if cp4ba_token != None:
            authValue : str = "Bearer "+cp4ba_token
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
            baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            urlExposed = hostUrl+baseUri+"/rest/bpm/wle/v1/exposed/process?excludeProcessStartUrl=false"
            response = requests.get(url=urlExposed, headers=my_headers, verify=False)
            if response.status_code == 200:
                data = response.json()["data"]
                exposedItemsList = data["exposedItemsList"]
                appProcName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
                appProcAcronym = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
                processNames = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_NAMES)
                appProcessNames = processNames.split(",")
                listOfProcessInfos = []
                for expIt in exposedItemsList:
                    if appProcName == expIt["processAppName"] and appProcAcronym == expIt["processAppAcronym"]:
                        if self.appId == None:
                            self.appId = expIt["processAppID"] 
                            self.bpdId = expIt["itemID"]
                        processName = expIt["display"]                        
                        for pn in appProcessNames:
                            if pn == processName:                        
                              listOfProcessInfos.append( bpmSys.BpmExposedProcessInfo(appProcName, appProcAcronym, processName, expIt["processAppID"], expIt["itemID"], expIt["startURL"]) )
                for appProcInfo in listOfProcessInfos:
                    key = appProcInfo.getAppProcessName()+"/"+appProcInfo.getAppName()+"/"+appProcInfo.getAppAcronym()
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
                        logging.error("%s error, user %s, status %d, error %s", self.contextName, self.userName, self.response.status_code, bpmErrorMessage)
                    except JSONDecodeError:
                        logging.error("%s error, user %s, response could not be decoded as JSON", self.contextName, self.user.userCreds.getName())
                        self.response.failure("Response could not be decoded as JSON")
                    except KeyError:
                        logging.error("%s error, user %s, response did not contain expected key 'Data', 'errorMessage'", self.contextName, self.user.userCreds.getName())
                        self.response.failure("Response did not contain expected key 'Data', 'errorMessage'")
