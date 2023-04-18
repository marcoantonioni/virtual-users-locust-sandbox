import bulkProcessOperations
import bawsys.commandLineManager as clpm
from bawsys import loadEnvironment as bawEnv
import sys, logging

#----------------------------------

def terminateProcessInstances(argv):
    ok = False
    if argv != None:
        bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:", ["environment="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()
            bulkOpsMgr = bulkProcessOperations.BpmProcessBulkOpsManager()
            bulkOpsMgr.terminateInstances(bpmEnvironment)
    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    terminateProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
