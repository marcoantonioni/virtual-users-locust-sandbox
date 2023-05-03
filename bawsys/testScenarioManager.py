import bawsys.loadEnvironment as bawEnv
import bawsys.bawSystem as bawSys
import bawsys.bawUtils as bawUtils
from bawsys.processInstanceManager import BpmProcessInstance
from bawsys.processInstanceManager import BpmProcessInstanceManager
from bawsys.processInstanceManager import BpmExecProcessInstance
import logging

class TestScenarioManager:
    tsMgr = None

    def __init__(self, bawEnv : bawEnv.BpmEnvironment):
        TestScenarioManager.tsMgr = self
        self.bpmEnvironment = bawEnv
        self.listOfPids = []
        self.startedAt = bawUtils._getDateTimeISO8601()

    @staticmethod
    def getInstance():
        return TestScenarioManager.tsMgr

    def addInstance(self, processInstanceInfo: BpmProcessInstance):
        self.listOfPids.append(processInstanceInfo.getPiid())

    def pollInstances(self, bpmProcessInstanceManager : BpmProcessInstanceManager):
        strNumProcesses = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_PROCESS_INSTANCES_MAX)
        terminateUnitTest = True
        if strNumProcesses != None:      
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
                        terminateUnitTest = True
            except BaseException as exception:
                logging.warning(f"Exception Name: {type(exception).__name__}")
                logging.warning(f"Exception Desc: {exception}")
                logging.error("Error polling instances.")
        return terminateUnitTest