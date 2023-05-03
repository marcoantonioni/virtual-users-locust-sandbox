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
        userName = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(self.bpmEnvironment)
        strNumProcesses = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_PROCESS_INSTANCES_MAX)
        terminateUnitTest = True
        if strNumProcesses != None:      
            try:
                numProcesses = int(strNumProcesses)   
                terminateUnitTest = False   
                if len(self.listOfPids) >= numProcesses:
                    print("have processes")
                    counter = 0
                    procInstance : BpmExecProcessInstance = None
                    for pid in self.listOfPids:
                        logging.info("getting status of [%s]", pid)                    
                        procInstance = bpmProcessInstanceManager.getProcessInstanceByPid(self.bpmEnvironment, pid, variables=False)
                        if procInstance != None:
                            strState = procInstance.executionState
                            if strState in ["Completed","Terminated","Failed"]:
                                counter += 1
                                print("counter:", counter)
                        else:
                            logging.error("Error getting process status for pid [%s]", pid)
                    # if completati
                    if counter >= numProcesses:
                        terminateUnitTest = True
            except BaseException as exception:
                logging.warning(f"Exception Name: {type(exception).__name__}")
                logging.warning(f"Exception Desc: {exception}")
                logging.error("Error polling instances.")
        return terminateUnitTest