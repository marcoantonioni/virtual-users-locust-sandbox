from bawsys import loadEnvironment as bpmEnv
from bawsys import bawUtils as bawUtils
from bawsys import testScenarioSqliteExport as sqlite
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
                self.dynamicAM.executeAsserts(listOfInstances)
                executed = True
        return executed


