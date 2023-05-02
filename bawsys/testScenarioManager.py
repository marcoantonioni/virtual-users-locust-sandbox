import bawsys.loadEnvironment as bawEnv
import bawsys.bawSystem as bawSys
from bawsys.processInstanceManager import BpmProcessInstance as bpmPI

class TestScenarioManager:
    def __init__(self, bawEnv : bawEnv.BpmEnvironment):
        self.bpmEnvironment = bawEnv
        self.listOfPids = []

    def addInstance(self, processInstanceInfo: bpmPI):
        self.listOfPids.append(processInstanceInfo.getPiid())

    def pollInstances(self):
        userName = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = self.bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(self.bpmEnvironment)

        print("TestScenarioManager polling instances", self.listOfPids)

        # /bas/rest/bpm/wle/v1/processes/search?statusFilter=Completed%2CFailed%2CTerminated&projectFilter=VUS

        return len(self.listOfPids) > 3
