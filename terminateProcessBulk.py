import bulkOperations
from bawsys import loadEnvironment as bawEnv

#----------------------------------

def terminateProcessInstances():
    bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()

    _fullPathBawEnv = "./configurations/env1.properties"
    bpmEnvironment.loadEnvironment(_fullPathBawEnv)
    bpmEnvironment.dumpValues()

    bulkOpsMgr = bulkOperations.BpmProcessBulkOpsManager()
    bulkOpsMgr.terminateInstances(bpmEnvironment)

def main():
    terminateProcessInstances()

if __name__ == "__main__":
    main()
