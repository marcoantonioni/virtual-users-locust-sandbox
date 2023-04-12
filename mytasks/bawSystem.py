
import requests, json
import mytasks.loadEnvironment as bpmEnv

class BpmExposedProcessInfo:
    def __init__(self, appName, appAcronym, processName, appId, appBpdId, startUrl):
        self.appName : str = appName
        self.appAcronym : str = appAcronym
        self.processName : str = processName
        self.appId : str = appId
        self.appBpdId : str = appBpdId
        self.startUrl : str = startUrl

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

    def getStartUrl(self):
        return self.startUrl

def _loginZen(self, bpmEnvironment : bpmEnv.BpmEnvironment, iamUrl: str, hostUrl: str):
    userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
    userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
    
    access_token : str = None
    token : str = None
    params : str = "grant_type=password&scope=openid&username="+userName+"&password="+userPassword
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    urlIdTk=iamUrl+"/idprovider/v1/auth/identitytoken"
    response = requests.post(url=urlIdTk, data=params, headers=my_headers, verify=False)
    if response.status_code == 200:
        access_token = response.json()["access_token"]
    if access_token != None:
        my_headers = {'username': userName, 'iam-token': access_token }
        response = requests.get(url=hostUrl+"/v1/preauth/validateAuth", headers=my_headers, verify=False)
        if response.status_code == 200:
            token = response.json()["accessToken"]
            return token
    return None
