"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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
    """
    Creates process instances based on the provided arguments.

    Parameters:
    argv (list): A list of command line arguments.

    Returns:
    None
    """    
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

            dynamicPLM : str = bpmEnvironment.getValue(bpmEnvironment.keyBAW_PAYLOAD_MANAGER)
            global bpmDynamicModule 
            try:
                bpmDynamicModule = bawUtils.import_module(dynamicPLM)
            except (ImportError, ModuleNotFoundError):
                print("Error module not found ", dynamicPLM)
                sys.exit()

            bpmPIM.BpmProcessInstanceManager._createProcessInstancesBatch(bpmEnvironment, bpmExposedProcessManager, bpmProcessInstanceManager, bpmDynamicModule, maxInstances, isLog=True)

    if ok == False:
        print("Wrong arguments, use -e 'filename' param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    createProcessInstances(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
