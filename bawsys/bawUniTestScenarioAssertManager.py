from bawsys import bawEnvironment as bpmEnv
from bawsys import bawUtils as bawUtils
from bawsys import bawUniTestScenarioAsserter as scenAsserter
from bawsys import bawUniTestScenarioSqliteExport as sqlite
import json, logging

class ScenarioAssertsManager:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment, bpmDynamicModuleAsserts):
        self.bpmEnvironment = bpmEnvironment
        self.dynamicAM = bpmDynamicModuleAsserts


    def executeAsserts(self):
        executed = False
        if self.dynamicAM != None:
            dbName = self.bpmEnvironment.getValue(self.bpmEnvironment.keyBAW_UNIT_TEST_OUT_SQLITEDB_NAME)
            dbMgr : sqlite.TestScenarioSqliteExporter = sqlite.TestScenarioSqliteExporter(dbName)
            listOfInstances = dbMgr.queryAll()
            if listOfInstances != None and len(listOfInstances) > 0:

                # crea asserter
                asserter = scenAsserter.ScenarioAsserter(self.bpmEnvironment)

                self.dynamicAM.executeAsserts(asserter, listOfInstances)


                logging.info("Now running unit tests...")
                
                if len(asserter.failures) == 0:
                    logging.info("Unit tests completed successfully !")
                else:
                    print("\nUnit tests failed !!!\n\n",
                            "==============================\n",
                            "Process instances analyzed:", 
                            len(listOfInstances), "\n", 
                            "==============================\n",
                            json.dumps(listOfInstances, indent=2), 
                            "\n\n",
                            "==============================\n",
                            "Failed assertions:", 
                            len(asserter.failures), "\n", 
                            "==============================\n",
                            json.dumps(asserter.failures, indent=2),"\n\n")

                executed = True                
        return executed


