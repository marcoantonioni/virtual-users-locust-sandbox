import bulkOperations
from bawsys import loadEnvironment as bawEnv

#----------------------------------

def deleteProcessInstances():
    bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()

    _fullPathBawEnv = "./configurations/env1.properties"
    bpmEnvironment.loadEnvironment(_fullPathBawEnv)
    bpmEnvironment.dumpValues()

    bulkOpsMgr = bulkOperations.BpmProcessBulkOpsManager()
    bulkOpsMgr.deleteInstances(bpmEnvironment, True)

def main():
    deleteProcessInstances()

if __name__ == "__main__":
    main()
