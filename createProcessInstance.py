import logging, sys, json, random, time
from bawsys import loadEnvironment as bpmEnv
import bawsys.commandLineManager as clpm
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import bawSystem as bawSys
import bawsys.processInstanceManager as bpmPIM
from base64 import b64encode
from bawsys import bawUtils as bawUtils 

bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
bpmProcessInstanceManager : bpmPIM.BpmProcessInstanceManager = bpmPIM.BpmProcessInstanceManager()


def createProcessInstances(argv):
    ok = False
    terminate = False
    if argv != None:
        bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:i:", ["environment=", "instances="])
        if cmdLineMgr.isExit() == False:
            ok = True
            maxInstances = 1
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _numInstances = cmdLineMgr.getParam("i", "instances")
            if _numInstances != None:
                maxInstances = int(_numInstances)
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()

            dynamicPLM : str = bpmEnvironment.getDynamicModuleFormatName()
            global bpmDynamicModule 
            bpmDynamicModule = bawUtils.import_module(dynamicPLM)

            bpmPIM.BpmProcessInstanceManager._createProcessInstancesBatch(bpmEnvironment, bpmExposedProcessManager, bpmProcessInstanceManager, bpmDynamicModule, maxInstances, isLog=True)
            #-----------------------
            """
            authorizationBearerToken = bpmExposedProcessManager.LoadProcessInstancesInfos(bpmEnvironment)

            userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
            userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
            runningTraditional = bawSys._isBawTraditional(bpmEnvironment)

            _headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            if runningTraditional == False:
                _headers['Authorization'] = 'Bearer '+authorizationBearerToken
            else:
                _headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

            processInfoKeys = bpmExposedProcessManager.getKeys()
            totalKeys = len(processInfoKeys)

            count = 0
            while count < maxInstances:
                rndIdx : int = random.randint(0, (totalKeys-1))
                key = processInfoKeys[rndIdx]
                processName = key.split("/")[0]
                processInfo = bpmExposedProcessManager.getProcessInfos(key)  
                jsonPayloadInfos = bpmDynamicModule.buildPayloadForSubject("Start-"+processName)
                jsonPayload = jsonPayloadInfos["jsonObject"]
                strPayload = json.dumps(jsonPayload)
                processInstanceInfo : bpmPIM.BpmProcessInstance = bpmProcessInstanceManager.createInstance(bpmEnvironment, runningTraditional, userName, processInfo, strPayload, _headers)
                if processInstanceInfo != None:
                    print("Created process "+processName+" instance id["+processInstanceInfo.getPiid()+"], state["+processInstanceInfo.getState()+"]")
                count += 1
            """
            #-------------------------------

    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    createProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
