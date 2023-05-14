"""
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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


