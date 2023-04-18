import logging, sys, json, importlib, random, time
from bawsys import loadEnvironment as bpmEnv
import bawsys.commandLineManager as clpm
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import bawSystem as bawSys
import mytasks.processInstanceManager as bpmPIM

bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
bpmProcessInstanceManager : bpmPIM.BpmProcessInstanceManager = bpmPIM.BpmProcessInstanceManager()

def import_module(name, package=None):
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
            bpmDynamicModule = import_module(dynamicPLM)

            bpmExposedProcessManager.LoadProcessInstancesInfos(bpmEnvironment)

            processInfoKeys = bpmExposedProcessManager.getKeys()
            totalKeys = len(processInfoKeys)

            count = 0
            maxInstances
            while count < maxInstances:
                rndIdx : int = random.randint(0, (totalKeys-1))
                key = processInfoKeys[rndIdx]
                processName = key.split("/")[0]
                processInfo = bpmExposedProcessManager.getProcessInfos(key)  
                jsonPayloadInfos = bpmDynamicModule.buildPayloadForSubject("Start-"+processName)
                
                jsonPayload = jsonPayloadInfos["jsonObject"]
                strPayload = json.dumps(jsonPayload)
                processInstanceInfo : bpmPIM.BpmProcessInstance = bpmProcessInstanceManager.createInstance(bpmEnvironment, processInfo, strPayload, None)
                if processInstanceInfo != None:
                    print("Created process "+processName+" instance id["+processInstanceInfo.getPiid()+"], state["+processInstanceInfo.getState()+"]")
                count += 1

    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    createProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
