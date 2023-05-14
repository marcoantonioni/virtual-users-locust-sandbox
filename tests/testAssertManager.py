import sys, logging
sys.path.append('.')

import bawsys.bawUniTestScenarioAssertManager as asserts
import bawsys.bawCommandLineManager as clpm
import bawsys.bawEnvironment as bawEnv
import bawsys.bawUtils as bawUtils

#----------------------------------

def testAssertsManager(argv):
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
            
            dynamicAM = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_ASSERTS_MANAGER)
            if dynamicAM != None and dynamicAM != "":
                try:
                    bpmDynamicModuleAsserts = bawUtils.import_module(dynamicAM)
                except (ImportError, ModuleNotFoundError):
                    logging.error("Error module not found [%s]", dynamicAM)
                    sys.exit()

                assertsMgr : asserts.ScenarioAssertsManager = asserts.ScenarioAssertsManager(bpmEnvironment, bpmDynamicModuleAsserts)
                assertsMgr.executeAsserts()

    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    testAssertsManager(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
