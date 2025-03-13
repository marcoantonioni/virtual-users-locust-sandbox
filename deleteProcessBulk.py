"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import bawsys.bawBulkProcessOperations as bulkOps
import bawsys.bawCommandLineManager as clpm
from bawsys import bawEnvironment as bawEnv
import sys, logging

#----------------------------------

def deleteProcessInstances(argv):
    """
    Delete process instances based on the provided arguments.

    Parameters:
    argv (list): A list of command line arguments.

    Returns:
    None
    """    
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
