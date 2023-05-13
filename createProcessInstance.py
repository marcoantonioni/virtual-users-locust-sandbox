import logging, sys, json, random, time
from bawsys import bawEnvironment as bpmEnv
import bawsys.bawCommandLineManager as clpm
import bawsys.bawExposedProcessManager as bpmExpProcs
from bawsys import bawSystem as bawSys
import bawsys.bawProcessInstanceManager as bpmPIM
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

    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    createProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
