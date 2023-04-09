

from jproperties import Properties

class BpmEnvironment:
    configFullPathName : str = None
    configValues : Properties = None

    keyBAW_IAM_HOST : str = "BAW_IAM_HOST"
    keyBAW_BASE_HOST : str = "BAW_BASE_HOST"

    def loadEnvironment(self, fullPathName):
        self.configFullPathName = fullPathName
        self.configValues = Properties()
        with open(self.configFullPathName, 'rb') as rRrops:
            self.configValues.load(rRrops)

    def getValue(self, key):
        return self.configValues.get(key).data

