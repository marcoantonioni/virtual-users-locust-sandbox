import time, random, json
from base64 import b64encode
from contextlib import redirect_stdout

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

def _writeOutInstances(listOfInstances, _fullPathNameOutput):
    instances = []
    if listOfInstances != None:
        numProcesses = len(listOfInstances)
        idx = 0
        while idx < numProcesses:
            instance = {}
            instance["processName"] = listOfInstances[idx].bpdName
            instance["processId"] = listOfInstances[idx].piid 
            instance["state"] = listOfInstances[idx].executionState
            instance["variables"] = listOfInstances[idx].variables
            instances.append(instance)                    
            idx += 1
    if _fullPathNameOutput != None and _fullPathNameOutput != "":
        with open(_fullPathNameOutput, 'w') as f:
            with redirect_stdout(f):
                print(json.dumps(instances, indent=2))
            f.close()
    else:
        print()
        print(json.dumps(instances, indent=2))
