from bawsys import loadEnvironment as bpmEnv
from bawsys import bawUtils as bawUtils
from bawsys import testScenarioAsserter as scenAsserter
from bawsys import testScenarioSqliteExport as sqlite
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


                #--------------------------
                # chiamata automatica da interno
                
                if len(asserter.failures) == 0:
                    print("\nTEST OK")
                else:
                    print("\nTEST FAILED\n\nItems", len(listOfInstances), "\n", 
                            json.dumps(listOfInstances, indent=2), 
                            "\n\nfailures", len(asserter.failures), "\n", 
                            json.dumps(asserter.failures, indent=2))

                executed = True                
        return executed


