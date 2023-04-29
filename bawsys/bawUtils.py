import time, random
from base64 import b64encode

def _getAttributeNamesFromDictionary(varDict):
    listOfVarNames = []
    varNames : dict = varDict.keys()
    for attrName in varDict.keys():
        listOfVarNames.append(attrName)
    return listOfVarNames

def _cleanVarData(varDict):
    listOfVarNames = _getAttributeNamesFromDictionary(varDict)
    for vn in listOfVarNames:
        vnObj = varDict[vn]
        if vnObj != None:
            if type(vnObj) == dict:
                _cleanVarData(vnObj)
                try:
                    del vnObj["@metadata"]
                except KeyError:
                    pass
    return varDict

def _extractPayloadOptionalThinkTime(payloadInfos: dict, user, wait: bool):
    payload = payloadInfos["jsonObject"]
    if wait == True:
        think : int = payloadInfos["thinkTime"]
        if ( think == -1):
            think : int = random.randint(user.min_think_time, user.max_think_time)
        time.sleep( think )
    return payload

def _basicAuthHeader(username, password):
    chSet : str = "latin1"
    username = username.encode(chSet)
    password = password.encode(chSet)
    return "Basic " + b64encode(b":".join((username, password))).strip().decode("ascii")
