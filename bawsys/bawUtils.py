"""
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import time, random, json, sys, importlib
from base64 import b64encode
from contextlib import redirect_stdout
from datetime import datetime

def _getDateTimeISO8601(dateTime = None):
    if dateTime == None:
        dateTime = datetime.now()
    return dateTime.strftime("%Y-%m-%dT%H:%M:%SZ")

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

def _writeOutScenarioInstances(listOfInstances, _fullPathNameOutput, startedAtISO, endedAtISO, numOfInstances, timeExceeded, assertsMgrName):
    if _fullPathNameOutput != None and _fullPathNameOutput != "":
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
        infos = {}
        infos["startedAt"] = startedAtISO
        infos["endedAt"] = endedAtISO
        infos["numOfInstances"] = numOfInstances
        infos["timeExceeded"] = False
        if timeExceeded == 1:
            infos["timeExceeded"] = True
        infos["assertsManager"] = assertsMgrName
        infos["instances"] = instances
        with open(_fullPathNameOutput, 'w') as f:
            with redirect_stdout(f):
                print(json.dumps(infos, indent=2))
            f.close()
    else:
        print()
        print(json.dumps(instances, indent=2))

def import_module(fname, package=None):
    spec = importlib.util.spec_from_file_location("module.name", fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = mod
    spec.loader.exec_module(mod)    
    return mod

"""
def import_module(name, package=None):
    print(name)
    absolute_name = importlib.util.resolve_name(name, package)
    try:
        return sys.modules[absolute_name]
    except KeyError:
        pass

    path = None
    if '.' in absolute_name:
        parent_name, _, child_name = absolute_name.rpartition('.')
        parent_module = import_module(parent_name)
        path = parent_module.__spec__.submodule_search_locations
    for finder in sys.meta_path:
        spec = finder.find_spec(absolute_name, path)
        if spec is not None:
            break
    else:
        msg = f'No module named {absolute_name!r}'
        raise ModuleNotFoundError(msg, name=absolute_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[absolute_name] = module
    spec.loader.exec_module(module)
    if path is not None:
        setattr(parent_module, child_name, module)
    return module
"""


def setupAssertsManagerModule(bpmEnvironment):
    bpmDynamicModuleAsserts = None
    strRunAssertsMagr = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_RUN_ASSERTS_MANAGER)
    if strRunAssertsMagr != None:
        if strRunAssertsMagr.lower() == "true":
            dynamicAM = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_ASSERTS_MANAGER)
            if dynamicAM != None and dynamicAM != "":
                bpmDynamicModuleAsserts = import_module(dynamicAM)
    return bpmDynamicModuleAsserts