
import requests, json, logging, sys, re, base64
import bawsys.loadEnvironment as bpmEnv
from requests.auth import HTTPBasicAuth

def getUserNumber( userId : str ):
    # se primo carattere numero errore
    if (userId[0] >= '0' and userId[0] <= '9') == True:
        return None
    
    # se ultimo carattere non numero errore
    lastChar = userId[len(userId)-1]
    if (lastChar >= '0' and lastChar <= '9') == False:
        return None
    
    matchNumbers = re.search(r'\d+', userId)
    matchStart = matchNumbers.start()
    userName = userId[0:matchStart]
    userNum = int ( matchNumbers.group() )
    return {'name': userName, 'number': userNum}

def usersRange( userId: str ):
    rangeOfUsers = None
    if userId.find("..") != -1:
        uSegs = userId.split("..")
        if len(uSegs) == 2:
            rangeOfUsers = { 'min': -1, 'max': -1}
            infoFrom = getUserNumber( uSegs[0] )
            infoTo = getUserNumber( uSegs[1] )
            if infoFrom["name"] == infoTo["name"]:
                if infoFrom["number"] <= infoTo["number"]:                
                    rangeOfUsers = {'infoFrom': infoFrom, 'infoTo': infoTo}
                else:
                    logging.error("ERROR: wrong sequence for user number in range definition, error in %s", userId)
                    sys.exit()
            else:
                logging.error("ERROR: wrong user names in range definition, error in %s", userId)
                sys.exit()

        else:
            logging.error("ERROR: wrong user range definition, error in %s", userId)
            sys.exit()
        pass
    return rangeOfUsers;

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

def _isBawTraditional( bpmEnvironment : bpmEnv.BpmEnvironment ):
    runTraditional = True
    runMode = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_TASK_LIST_STRATEGY)    
    if runMode == bpmEnv.BpmEnvironment.valBAW_TASK_LIST_STRATEGY_FEDERATEDPORTAL:
        runTraditional = False
    return runTraditional

def _loginZen(bpmEnvironment : bpmEnv.BpmEnvironment, iamUrl: str, hostUrl: str):
    userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
    userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
    if iamUrl.endswith('/'):
        iamUrl = iamUrl[:-1]
    if hostUrl.endswith('/'):
        hostUrl = hostUrl[:-1]
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

def _loginTraditional(bpmEnvironment : bpmEnv.BpmEnvironment, hostUrl: str, userName: str, userPassword: str):
    if hostUrl.endswith('/'):
        hostUrl = hostUrl[:-1]
    baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
    if baseUri == None:
        baseUri = ""
    my_headers = {'Accept': 'application/json'}    
    fullUrl = hostUrl+baseUri+"/rest/bpm/wle/v1/user/current?includeInternalMemberships=false&includeEditableUserPreferences=false&parts=none"
    response = requests.get(url=fullUrl, headers=my_headers, verify=False, auth = HTTPBasicAuth(userName, userPassword) )
    if response.status_code == 200:
        return response.cookies
    else:
        logging.error("_loginTraditional", response.status_code, response.text)
        
    return None
