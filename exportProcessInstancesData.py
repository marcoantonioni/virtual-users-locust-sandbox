import bawsys.commandLineManager as clpm
import bawsys.processInstanceManager as bawPIM
from bawsys import loadEnvironment as bawEnv
import sys, logging, json
from contextlib import redirect_stdout

#----------------------------------

def listProcessInstances(argv):
    ok = False
    terminate = False
    if argv != None:
        bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:s:f:t:n:o:", ["environment=", "status=", "from=", "to=", "name=", "output="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _status = cmdLineMgr.getParam("s", "status")
            _dateFrom = cmdLineMgr.getParam("f", "from")
            _dateTo = cmdLineMgr.getParam("t", "to")
            _bpdName = cmdLineMgr.getParam("n", "name")
            _fullPathNameOutput = cmdLineMgr.getParam("o", "output")

            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()

            pim = bawPIM.BpmProcessInstanceManager()
            listOfInstances = pim.exportProcessInstancesData(bpmEnvironment, _bpdName, _status, _dateFrom, _dateTo)

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
            
    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file, use -s for status Completed,Terminated,Failed, dateFrom and dateTo using format AAAA-MM-DDThh:mm:ssZ, -o to save rusults to file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    listProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
