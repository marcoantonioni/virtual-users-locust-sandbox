import bawsys.loadEnvironment as bawEnv
import bawsys.bawSystem as bawSys
import bawsys.bawUtils as bawUtils
from bawsys.processInstanceManager import BpmProcessInstance
from bawsys.processInstanceManager import BpmProcessInstanceManager
from bawsys.processInstanceManager import BpmExecProcessInstance
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