import bawsys.bawCommandLineManager as clpm
import bawsys.bawProcessInstanceManager as bawPIM
from bawsys import bawEnvironment as bawEnv
from bawsys import bawUtils as bawUtilities
import sys, logging, json

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
            bawUtilities._writeOutScenarioInstances(listOfInstances, _fullPathNameOutput, "", "", len(listOfInstances), 0 , "")
            
    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file, use -s for status Completed,Terminated,Failed, dateFrom and dateTo using format AAAA-MM-DDThh:mm:ssZ, -o to save rusults to file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    listProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
