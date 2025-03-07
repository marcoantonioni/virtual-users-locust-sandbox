"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import bawsys.bawEnvironment as bawEnv
import bawsys.bawSystem as bawSys
import bawsys.bawUtils as bawUtils
from bawsys.bawProcessInstanceManager import BpmProcessInstance
from bawsys.bawProcessInstanceManager import BpmProcessInstanceManager
from bawsys.bawProcessInstanceManager import BpmExecProcessInstance
import logging
from datetime import datetime

class TestScenarioManager:
    tsMgr = None

    def __init__(self, bawEnv : bawEnv.BpmEnvironment):
        TestScenarioManager.tsMgr = self
        self.bpmEnvironment = bawEnv
        self.listOfPids = []
        self.startedAt = datetime.now()
        self.endedAt = None
        self.startedAtISO = bawUtils._getDateTimeISO8601(self.startedAt)
        self.endedAtISO = None
        self.timeLimitExceeded = False

    @staticmethod
    def getInstance():
        return TestScenarioManager.tsMgr

    def addInstance(self, processInstanceInfo: BpmProcessInstance):
        self.listOfPids.append(processInstanceInfo.getPiid())

    def pollInstances(self, bpmProcessInstanceManager : BpmProcessInstanceManager):
        terminateUnitTest = True
        strNumProcesses = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_PROCESS_INSTANCES_MAX)
        if strNumProcesses != None:      
            strMaxDuration = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_UNIT_TEST_MAX_DURATION);
            maxDuration = 5
            if strMaxDuration != None:
                maxDuration = int(strMaxDuration)
                self.endedAt = datetime.now()
                deltaTime = self.endedAt - self.startedAt
                self.timeLimitExceeded = (deltaTime.total_seconds() / 60) >= maxDuration
                if self.timeLimitExceeded:
                    self.endedAtISO = bawUtils._getDateTimeISO8601(self.endedAt)
                    logging.debug("Unit test scenario exceeded the configured time limit")
                    return terminateUnitTest
            try:
                numProcesses = int(strNumProcesses)   
                terminateUnitTest = False   
                if len(self.listOfPids) >= numProcesses:
                    counter = 0
                    procInstance : BpmExecProcessInstance = None
                    for pid in self.listOfPids:
                        procInstance = bpmProcessInstanceManager.getProcessInstanceByPid(self.bpmEnvironment, pid, variables=False)
                        if procInstance != None:
                            strState = procInstance.executionState
                            if strState in ["Completed","Terminated","Failed"]:
                                counter += 1
                        else:
                            logging.error("Error getting process status for pid [%s]", pid)
                    if counter >= numProcesses:
                        self.endedAt = datetime.now()
                        self.endedAtISO = bawUtils._getDateTimeISO8601(self.endedAt)
                        terminateUnitTest = True
            except BaseException as exception:
                logging.warning(f"Exception Name: {type(exception).__name__}")
                logging.warning(f"Exception Desc: {exception}")
                logging.error("Error polling instances.")
        return terminateUnitTest