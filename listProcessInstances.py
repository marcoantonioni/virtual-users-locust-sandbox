import bawsys.bawCommandLineManager as clpm
import bawsys.bawProcessInstanceManager as bawPIM
from bawsys import bawEnvironment as bawEnv
import sys, logging

#----------------------------------

def listProcessInstances(argv):
    ok = False
    terminate = False
    if argv != None:
        bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:s:f:t:", ["environment=", "status=", "from", "to"])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _status = cmdLineMgr.getParam("s", "status")
            _dateFrom = cmdLineMgr.getParam("f", "from")
            _dateTo = cmdLineMgr.getParam("t", "to")

            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()

            pim = bawPIM.BpmProcessInstanceManager()
            
            # _status = "Terminated"
            # _status = "Active,Completed,Failed,Terminated"
            # _dateFrom = "2023-04-01T00:00:00Z"
            # _dateTo = "2023-04-30T00:00:00Z"
            listOfInstances = pim.searchProcessInstances(bpmEnvironment, _status, _dateFrom, _dateTo)

            if listOfInstances != None:
                numProcesses = len(listOfInstances)
                idx = 0
                while idx < numProcesses:
                    print("process ", listOfInstances[idx].piid, listOfInstances[idx].bpdName, listOfInstances[idx].executionState)
                    idx += 1

    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file, use -s for status Completed,Terminated,Failed, dateFrom and dateTo using format AAAA-MM-DDThh:mm:ssZ")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    listProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
