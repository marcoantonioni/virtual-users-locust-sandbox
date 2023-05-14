from bawsys import bawEnvironment as bpmEnv
from bawsys import bawUtils as bawUtils
from bawsys import bawUniTestScenarioAsserter as scenAsserter
from bawsys import bawUniTestScenarioSqliteExport as sqlite
import json, logging, os
from contextlib import redirect_stdout

class ScenarioAssertsManager:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment, bpmDynamicModuleAsserts):
        self.bpmEnvironment = bpmEnvironment
        self.dynamicAM = bpmDynamicModuleAsserts


    def executeAsserts(self):
        executed = False
        if self.dynamicAM != None:
            dbName = self.bpmEnvironment.getValue(self.bpmEnvironment.keyBAW_UNIT_TEST_OUT_SQLITEDB_NAME)
            failuresName = self.bpmEnvironment.getValue(self.bpmEnvironment.keyBAW_UNIT_TEST_OUT_FILE_NAME)+".failures"
            dbMgr : sqlite.TestScenarioSqliteExporter = sqlite.TestScenarioSqliteExporter(dbName)
            listOfInstances = dbMgr.queryAll()
            if listOfInstances == None:
                listOfInstances = []
            # crea asserter
            asserter = scenAsserter.ScenarioAsserter(self.bpmEnvironment)
            logging.info("Now running unit tests...")
            try:
                self.dynamicAM.executeAsserts(asserter, listOfInstances)
                if len(asserter.failures) == 0:
                    os.remove(failuresName)
                    logging.info("Unit tests completed successfully !")                    
                else:
                    # predisporre out su file                    
                    with open(failuresName, 'w') as f:
                        with redirect_stdout(f):
                            print("\nUnit tests failed at "+bawUtils._getDateTimeISO8601()+" !!!\n\n",
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
                        f.close()

                    logging.info("Unit tests failed ! For details see file %s", failuresName)
                    executed = True                
            except BaseException as exception:
                logging.warning(f"Exception Name: {type(exception).__name__}")
                logging.warning(f"Exception Desc: {exception}")
                logging.error("ERROR, exception catched during assertions !!!")
        return executed


