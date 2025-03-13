"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import bawsys.bawCommandLineManager as clpm
import bawsys.bawProcessInstanceManager as bawPIM
from bawsys import bawEnvironment as bawEnv
from bawsys import bawUtils as bawUtilities
import sys, logging, json

#----------------------------------


def exportProcessInstancesData(argv):
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
    exportProcessInstancesData(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
