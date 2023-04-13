
import logging
from jproperties import Properties

class BpmEnvironment:
    configFullPathName : str = None
    configValues : Properties = None

    keyBAW_IAM_HOST : str = "BAW_IAM_HOST"
    keyBAW_BASE_HOST : str = "BAW_BASE_HOST"

    keyBAW_USERS_STRATEGY : str = "BAW_USERS_STRATEGY"
    valBAW_USERS_STRATEGY_UNIQUE : str = "UNIQUE"
    valBAW_USERS_STRATEGY_TWINS : str = "TWINS"

    keyBAW_TASK_LIST_STRATEGY : str = "BAW_TASK_LIST_STRATEGY"
    valBAW_TASK_LIST_STRATEGY_STANDALONE : str = "STANDALONE"
    valBAW_TASK_LIST_STRATEGY_FEDERATEDPORTAL : str = "FEDERATEDPORTAL"

    keyBAW_BASE_URI_SERVER : str = "BAW_BASE_URI_SERVER"

    keyBAW_PROCESS_APPLICATION_NAME : str = "BAW_PROCESS_APPLICATION_NAME"
    keyBAW_PROCESS_APPLICATION_ACRONYM : str = "BAW_PROCESS_APPLICATION_ACRONYM"
    keyBAW_PROCESS_NAMES : str = "BAW_PROCESS_NAMES"

    keyBAW_VU_THINK_TIME_MIN : str = "BAW_VU_THINK_TIME_MIN"
    keyBAW_VU_THINK_TIME_MAX : str = "BAW_VU_THINK_TIME_MAX"

    keyBAW_POWER_USER_NAME : str = "BAW_POWER_USER_NAME"
    keyBAW_POWER_USER_PASSWORD : str = "BAW_POWER_USER_PASSWORD"

    keyBAW_VU_ACTIONS : str = "BAW_VU_ACTIONS"

    keyBAW_ACTION_LOGIN="LOGIN"
    keyBAW_ACTION_CLAIM="CLAIM"
    keyBAW_ACTION_COMPLETE="COMPLETE"
    keyBAW_ACTION_GETDATA="GETDATA"
    keyBAW_ACTION_SETDATA="SETDATA"
    keyBAW_ACTION_RELEASE="RELEASE"
    keyBAW_ACTION_CREATEPROCESS="CREATEPROCESS"
    keyBAW_ALL_ACTIONS=keyBAW_ACTION_LOGIN+","+keyBAW_ACTION_CLAIM+","+keyBAW_ACTION_COMPLETE+","+keyBAW_ACTION_GETDATA+","+keyBAW_ACTION_SETDATA+","+keyBAW_ACTION_RELEASE+","+keyBAW_ACTION_CREATEPROCESS
    keyBAW_ACTION_ACTIVATED="YES"
    
    def loadEnvironment(self, fullPathName):
        self.configFullPathName = fullPathName
        self.configValues = Properties()
        with open(self.configFullPathName, 'rb') as rRrops:
            self.configValues.load(rRrops)

    def getValue(self, key):
        data = None
        cfgVal = self.configValues.get(key)
        if cfgVal != None:
            data = cfgVal.data
        return data

    def dumpValues(self):
        logging.info("*** BAW ENVIRONMENT ***")
        for k in self.configValues.keys():
            cfgVal = self.configValues.get(k)
            if cfgVal != None:
                logging.info("%s=%s", k, cfgVal.data)
        logging.info("***********************")
