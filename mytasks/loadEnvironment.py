
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


    def loadEnvironment(self, fullPathName):
        self.configFullPathName = fullPathName
        self.configValues = Properties()
        with open(self.configFullPathName, 'rb') as rRrops:
            self.configValues.load(rRrops)

    def getValue(self, key):
        return self.configValues.get(key).data

    def dumpValues(self):
        logging.info("*** BAW ENVIRONMENT ***")
        for k in self.configValues.keys():
            logging.info("%s=%s", k, self.configValues.get(k).data)
        logging.info("***********************")
