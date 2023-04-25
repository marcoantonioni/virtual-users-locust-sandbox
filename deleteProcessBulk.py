import bawsys.bulkProcessOperations as bulkOps
import bawsys.commandLineManager as clpm
from bawsys import loadEnvironment as bawEnv
import sys, logging

#----------------------------------

def deleteProcessInstances(argv):
    ok = False
    terminate = False
    if argv != None:
        bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:t:", ["environment=", "terminate="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _term = cmdLineMgr.getParam("t", "terminate")
            terminate = _term == "true"
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()
            bulkOpsMgr = bulkOps.BpmProcessBulkOpsManager(bpmEnvironment)
            bulkOpsMgr.deleteInstances(terminate)
    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file, use -t true to terminate process instances before delete")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    deleteProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
