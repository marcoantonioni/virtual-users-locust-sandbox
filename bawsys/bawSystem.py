
import requests, random, logging, sys, re, base64, json
from json import JSONDecodeError
import bawsys.loadEnvironment as bpmEnv
from requests.auth import HTTPBasicAuth

#==========================================================================

class BpmExposedProcessInfo:
    def __init__(self, appName, appAcronym, snapshotName, tip, processName, appId, appBpdId, startUrl):
        self.appName : str = appName
        self.appAcronym : str = appAcronym
        self.snapshotName : str = snapshotName
        self.tip : bool = tip
        self.processName : str = processName
        self.appId : str = appId
        self.appBpdId : str = appBpdId
        self.startUrl : str = startUrl

        print(appName+", "+appAcronym+", "+snapshotName+", "+str(tip)+", "+processName+", "+appId+", "+appBpdId)

    def getAppName(self):
        return self.appName
    
    def getAppAcronym(self):
        return self.appAcronym
    
    def getSnapshotName(self):
        return self.snapshotName
    
    def isTip(self):
        return self.tip
    
    def getAppProcessName(self):
        return self.processName
    
    def getAppId(self):
        return self.appId
    
    def getAppBpdId(self):
        return self.appBpdId

    def getStartUrl(self):
        return self.startUrl

class BpmFederatedSystem:
    restUrlPrefix : str = None # /...server-base-uri.../rest/bpm/wle
    systemID : str = None
    displayName : str = None
    systemType : str = None # SYSTEM_TYPE_WLE | SYSTEM_TYPE_CASE
    id : str = None
    taskCompletionUrlPrefix : str = None # /...server-base-uri.../teamworks
    version : str = None
    indexRefreshInterval : int = 0
    statusCode : str = None
    targetObjectStoreName : str = None # present only if systemType==SYSTEM_TYPE_CASE

    def __init__(self, restUrlPrefix, systemID, displayName, systemType, id, taskCompletionUrlPrefix, version, indexRefreshInterval, statusCode, targetObjectStoreName):
        self.restUrlPrefix = restUrlPrefix
        self.systemID = systemID
        self.displayName = displayName
        self.systemType = systemType
        self.id = id
        self.taskCompletionUrlPrefix = taskCompletionUrlPrefix
        self.version = version
        self.indexRefreshInterval = indexRefreshInterval
        self.statusCode = statusCode
        self.targetObjectStoreName = targetObjectStoreName

    def getSystemID(self):
        return self.systemID

    def getRestUrlPrefix(self):
        return self.restUrlPrefix

    def getStatusCode(self):
        return self.statusCode

class BpmTask:
    id : str = None
    subject : str = None
    status : str = None
    state: str = None
    role: str = None
    systemID: str = None
    variableNames = []
    actions = []
    data: dict = None
    federatedSystem : BpmFederatedSystem = None

    def __init__(self, id, subject, status, state, role, systemID):
        self.id = id
        self.subject = subject
        self.status = status
        self.state = state
        self.role = role
        self.systemID = systemID

    def getId(self):
        return self.id

    def getSubject(self):
        return self.subject
    
    def getStatus(self):
        return self.status
    
    def getState(self):
        return self.state
    def setState(self, state):
        self.state = state
    
    def getRole(self):
        return self.role

    def getSystemID(self):
        return self.systemID

    def getVariableNames(self):
        return self.variableNames
    def setVariableNames(self, variableNames):
        self.variableNames = variableNames

    def getActions(self):
        return self.actions
    
    def setActions(self, actions):
        self.actions = actions

    def hasAction(self, action):
        for act in self.actions:
            if act == action:
                return True
        return False
    
    def setTaskData(self, data):
        self.data = data

    def getTaskData(self):
        return self.data

    def setFederatedSystem(self, fedSys):
        self.federatedSystem = fedSys

    def getFederatedSystem(self):
        return self.federatedSystem

    def isFederatedSystem(self):
        return self.federatedSystem != None

    def buildListOfVarNames(self):
        paramVarNames = ""
        allNames = self.getVariableNames()
        totNames = len(allNames)
        for pName in allNames:
            paramVarNames = paramVarNames + pName
            totNames = totNames - 1
            if totNames > 0:
                paramVarNames = paramVarNames + ","
        return paramVarNames

class BpmTaskList:
    count : int = 0
    bpmTasks : BpmTask = None
    bpmFederatedSystems = dict()

    def __init__(self, count, bpmTasks):
        self.count = count
        self.bpmTasks = bpmTasks

    def getCount(self):
        return self.count

    def getTasks(self):
        return self.bpmTasks
    
    def getPreparedTask( self, idx ):
        bpmTask : BpmTask = self.getTasks()[idx];
        if bpmTask != None:
            if bpmTask.getSystemID() != "":
                bpmTask.setFederatedSystem(self.bpmFederatedSystems[bpmTask.getSystemID()])
        return bpmTask
    
    def getPreparedTaskRandom(self):
        idx : int = random.randint(0, self.getCount()-1)
        return self.getPreparedTask( idx )
    
    def setFederationInfos( self, listOfBpmSystems ):
        for bpmSystem in listOfBpmSystems:
            targetObjectStoreName = None
            systemType = bpmSystem["systemType"]
            if systemType == "SYSTEM_TYPE_CASE":
                targetObjectStoreName = bpmSystem["targetObjectStoreName"]
            bpmFedSys : BpmFederatedSystem = BpmFederatedSystem(bpmSystem["restUrlPrefix"], bpmSystem["systemID"], bpmSystem["displayName"], systemType, bpmSystem["id"], bpmSystem["taskCompletionUrlPrefix"], bpmSystem["version"], bpmSystem["indexRefreshInterval"], bpmSystem["statusCode"], targetObjectStoreName)
            self.bpmFederatedSystems[bpmFedSys.getSystemID()] = bpmFedSys

#==========================================================================


# Identity token - address (cp-console)
def _identityToken(self, baseHost, userName, userPassword):
    idTk : str = None
    params : str = "grant_type=password&scope=openid&username="+userName+"&password="+userPassword
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    with self.client.post(url=baseHost+"/idprovider/v1/auth/identitytoken", data=params, headers=my_headers, catch_response=True) as response:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("_identityToken status code: %s", response.status_code)
        if response.status_code == 200:
            try:
                idTk = response.json()["access_token"]                
            except JSONDecodeError:
                logging.error("_identityToken error, user %s, response could not be decoded as JSON", userName)
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                logging.error("_identityToken error, user %s, did not contain expected key 'access_token'", userName)
                response.failure("Response did not contain expected key 'access_token'")
    return idTk

# Zen token - address (cpd-cp4ba)
def _zenToken(self, baseHost, userName, iamToken):
    zenTk : str = None
    my_headers = {'username': userName, 'iam-token': iamToken }
    
    with self.client.get(url=baseHost+"/v1/preauth/validateAuth", headers=my_headers, catch_response=True) as response:
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("_cp4baToken status code: %s", response.status_code)
        if response.status_code == 200:
            try:
                zenTk = response.json()["accessToken"]                
            except JSONDecodeError:
                logging.error("_cp4baToken error, user %s, response could not be decoded as JSON", userName)
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                logging.error("_cp4baToken error, user %s, did not contain expected key 'accessToken'", userName)
                response.failure("Response did not contain expected key 'accessToken'")
    return zenTk

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

def _isBawTraditional( bpmEnvironment : bpmEnv.BpmEnvironment ):
    runTraditional = False
    runMode = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_TASK_LIST_STRATEGY)    
    if runMode == bpmEnv.BpmEnvironment.valBAW_TASK_LIST_STRATEGY_STANDALONE:
        runTraditional = True
    return runTraditional

def _loginZen(bpmEnvironment : bpmEnv.BpmEnvironment, userName = None, userPassword = None):
    iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
    hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
    if userName == None or userPassword == None:
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

def _loginTraditional(bpmEnvironment : bpmEnv.BpmEnvironment, userName: str, userPassword: str):
    hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
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
