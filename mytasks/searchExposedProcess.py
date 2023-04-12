import requests, json
import mytasks.loadEnvironment as bpmEnv

requests.packages.urllib3.disable_warnings() 

class BpmExposedProcessInfo:
    def __init__(self, appName, appAcronym, processName, appId, appBpdId):
        self.appName = appName
        self.appAcronym = appAcronym
        self.processName = processName
        self.appId = appId
        self.appBpdId = appBpdId

    def getAppName(self):
        return self.appName
    
    def getAppAcronym(self):
        return self.appAcronym
    
    def getAppProcessName(self):
        return self.processName
    
    def getAppId(self):
        return self.appId
    
    def getAppBpdId(self):
        return self.appBpdId

class BpmExposedProcessManager:
    exposedProcesses = dict()

    def __init__(self):
      self.exposedProcesses = dict()

    def addProcessInfos(self, key: str, processInfo: BpmExposedProcessInfo):
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
    
    def LoadProcessInstancesInfos(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        
        access_token : str = None
        cp4ba_token : str = None
        params : str = "grant_type=password&scope=openid&username="+userName+"&password="+userPassword
        my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
        urlIdTk=iamUrl+"/idprovider/v1/auth/identitytoken"
        response = requests.post(url=urlIdTk, data=params, headers=my_headers, verify=False)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
        if access_token != None:
            cp4ba_token : str = None
            my_headers = {'username': userName, 'iam-token': access_token }
            response = requests.get(url=hostUrl+"/v1/preauth/validateAuth", headers=my_headers, verify=False)
            if response.status_code == 200:
                cp4ba_token = response.json()["accessToken"]
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
                            processName = expIt["display"]
                            for pn in appProcessNames:
                                if pn == processName:                        
                                  listOfProcessInfos.append( BpmExposedProcessInfo(appProcName, appProcAcronym, processName, expIt["processAppID"], expIt["itemID"]) )
                    for appProcInfo in listOfProcessInfos:
                        key = appProcInfo.getAppProcessName()+"/"+appProcInfo.getAppName()+"/"+appProcInfo.getAppAcronym()
                        self.addProcessInfos(key, appProcInfo)
                else:
                    print(response.status_code)
                    print(response.text)                
    pass
