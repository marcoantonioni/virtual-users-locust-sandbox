import bawsys.commandLineManager as clpm
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
import urllib, requests, json, sys, logging
from base64 import b64encode
from bawsys import bawUtils as bawUtils 

#----------------------------------

class DataTypeTemplate:
    def __init__(self, dtName: str, dtId: str, snapId: str, appId: str, properties):
        self.dtName : str = dtName
        self.dtId : str = dtId
        self.dtSnapId : str = snapId
        self.appId : str = appId
        self.properties : str = properties
        self.templateBuilt = False
        self.dtTypeTemplate = '{"varName":{}}'

    def getClassRefKey(self):
        return self.dtId+"/"+self.dtSnapId

    def buildClassRefKey(self, pdtId, pdtSnapId):
        return pdtId+"/"+pdtSnapId

    def buildJsonArribute(self, pName: str, pClass: str, pIsArr: bool, referencedTypeName: str):
        templatePayload = ""
        templIdxVal = ""

        attrVal = '""'
        if pClass == "Boolean":
            attrVal = "false"
            
        if pClass == "Integer":
            attrVal = "0"
            
        if referencedTypeName != None:
            attrVal = '{}'

        if pIsArr == True:
            templatePayload = '"'+pName+'": ['+attrVal+']'
        else:
            templatePayload = '"'+pName+'": '+attrVal
        return templatePayload

    """
    def buildJsonArributeTemplate(self, idxTemplate: int, pName: str, pClass: str, pIsArr: bool, pClassRef: str, pClasSnapId: str, referencedTypeName: str):
        templatePayload = ""
        templIdxVal = ""
        if referencedTypeName != None:
            templIdxVal = "@@@-"+str(idxTemplate)+"-@@@-type("+referencedTypeName+")"
        else:
            templIdxVal = "@@@-"+str(idxTemplate)+"-@@@"
        if pIsArr == True:
            templatePayload = '\"'+pName+'":["'+templIdxVal+'"]'
        else:
            templatePayload = '\"'+pName+'":"'+templIdxVal+'"'
        return templatePayload
    """

    def builTemplate(self, dataTypeTemplates: dict, dataTypeTemplatesByClassRef: dict):
        self.templateBuilt = True
        referencedTypes = []
        idxTemplate = 1
        attribs = ""
        tot = len(self.properties)
        for prop in self.properties:
            pName = prop["name"]
            pClass = prop["typeClass"]
            pIsArr = prop["isArray"]
            isArr = "False"
            if pIsArr == True:
                isArr = "True"
            pClassRef = None
            pClasSnapId = None
            referencedType: DataTypeTemplate = None

            try:
                pClassRef = prop["typeClassRef"]
                if pClassRef != None:
                    pClasSnapId = prop["typeClassSnapshotId"]
                    referencedType = dataTypeTemplatesByClassRef[self.buildClassRefKey(pClassRef, pClasSnapId)]
            except KeyError:
                pass

            referencedTypeName = None
            if referencedType != None:
                referencedTypeName = referencedType.dtName                       

            # attrib = self.buildJsonArributeTemplate(idxTemplate, pName, pClass, pIsArr, pClassRef, pClasSnapId, referencedTypeName)
            if referencedTypeName != None:
                referencedTypes.append('\''+pName+'\' of type '+referencedTypeName)
            attrib = self.buildJsonArribute(pName, pClass, pIsArr, referencedTypeName)
            attribs += attrib
            if (tot > 1):
                attribs += ", "
            idxTemplate = idxTemplate + 1
            tot = tot -1
        refs = "#==========================\n# Create "+self.dtName+" json object\n" 
        for r in referencedTypes:
            refs += '# '+r
            refs += "\n"
        self.dtTypeTemplate = refs+'def new'+self.dtName+'():\n    return {'+attribs+'}'

class PayloadTemplateManager:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        self.dataTypeTemplates = dict()
        self.dataTypeTemplatesByClassRef = dict()
        self.appAcronym = None
        self.appName = None
        self.appSnapName = None 
        self.appSnapTip = None
        self.useTip = False

        self.loggedIn = False
        self.authorizationBearerToken : str = None
        self.cookieTraditional = None
        self.bpmEnvironment = bpmEnvironment
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(bpmEnvironment)
        if runningTraditional == True:
            self.cookieTraditional = bawSys._loginTraditional(self.bpmEnvironment, userName, userPassword)
            if self.cookieTraditional != None:
                self.loggedIn = True
        else:
            self.authorizationBearerToken = bawSys._loginZen(self.bpmEnvironment, userName, userPassword)
            if self.authorizationBearerToken != None:
                self.loggedIn = True

        if self.loggedIn == True:
            if runningTraditional == False:
                self._headers['Authorization'] = 'Bearer '+self.authorizationBearerToken
            else:
                self._headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

    def buildDataTypeTemplates(self, hostUrl, baseUri, dtName, dtId, snapId, appId):

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        uriData = dtId+"?snapshotId="+snapId+"&processAppId="+appId
        urlDataType = hostUrl+uriBaseRest+"/businessobject/"+uriData

        response = requests.get(url=urlDataType, headers=self._headers, verify=False)
        if response.status_code == 200:
            data = response.json()["data"]
            properties = data["properties"]
            dtTempl = DataTypeTemplate(dtName, dtId, snapId, appId, properties)
            self.dataTypeTemplates[dtName] = dtTempl            
            self.dataTypeTemplatesByClassRef[dtTempl.getClassRefKey()] = dtTempl

    def getModel(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
        bpmExposedProcessManager.LoadProcessInstancesInfos(self.bpmEnvironment)
        appId = bpmExposedProcessManager.getAppId()
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

        self.appAcronym : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
        self.appName : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
        self.appSnapName : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
        self.appSnapTip : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP)
        self.useTip = False
        if self.appSnapTip.lower() == "true":
            self.useTip = True
        if self.appSnapName == None or self.appSnapName == "":
            self.useTip = True

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"


        # legge applicazioni
        applicationInfo : bawSys.ApplicationInfo = None
        urlApps = hostUrl+uriBaseRest+"/processApps"
        response = requests.get(url=urlApps, headers=self._headers, verify=False)
        if response.status_code == 200:
            data = response.json()["data"]
            processAppsList = data["processAppsList"]
            for app in processAppsList:
                if app["shortName"] == self.appAcronym and app["name"] == self.appName:
                    applicationInfo = bawSys.ApplicationInfo(app)
                    break

            if applicationInfo != None:
                # legge assets
                urlAssetts = hostUrl+uriBaseRest+"/assets?processAppId="+applicationInfo.appId

                if self.useTip == False:
                    for appVer in applicationInfo.versions:
                        if appVer.snapName == self.appSnapName and appVer.snapTip == False:
                            urlAssetts += "&snapshotId="+appVer.snapId+"&branchId="+appVer.snapBranchID
                            break
            else:
                logging.error("Error, application not found")
                sys.exit()

            response = requests.get(url=urlAssetts, headers=self._headers, verify=False)
            if response.status_code == 200:
                data = response.json()["data"]
                snapshotId = data["snapshotId"]
                dataTypesList = data["VariableType"]
                for dataType in dataTypesList:
                    dtName = dataType["name"]
                    dtId = dataType["poId"]
                    self.buildDataTypeTemplates(hostUrl, baseUri, dtName, dtId, snapshotId, appId)
            else:
                print("ERROR, status code: ", response.status_code)
                print(json.dumps(response.json(), indent = 2))

    def buildTypeTemplate(self):
        for dtName in self.dataTypeTemplates.keys():
            dtTemplate : DataTypeTemplate = self.dataTypeTemplates[dtName]
            dtTemplate.builTemplate(self.dataTypeTemplates, self.dataTypeTemplatesByClassRef)

    def generateTemplates(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        # load all data types, add in allDataTypes dict using boId+boSnapId key
        self.getModel(bpmEnvironment)
        # build data type template
        self.buildTypeTemplate()

    def printDataTypes(self, _indentOutput: str):
        indent = False
        if _indentOutput != None:
            indent = _indentOutput.lower() == "true"
        print("# ==================================")
        print("# Python code for data model objects\n# Application ["+self.appName+"] Acronym ["+self.appAcronym+"] Snapshot ["+self.appSnapName+"] Tip ["+self.appSnapTip+"]")
        print("# ==================================\n")
        for dtName in self.dataTypeTemplates.keys():
            dtTemplate : DataTypeTemplate = self.dataTypeTemplates[dtName]
            """
            payloadTemplate = None
            if indent == True:
                payloadTemplate = json.dumps( json.loads(dtTemplate.dtTypeTemplate), indent = 2)
            else:
                payloadTemplate = dtTemplate.dtTypeTemplate
            """
            payloadTemplate = dtTemplate.dtTypeTemplate
            
            print(payloadTemplate+"\n")

            print()

def generatePayloadTemplates(argv):

    ok = False
    if argv != None:
        bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:i:", ["environment=", "indent="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _indentOutput = cmdLineMgr.getParam("i", "indent")
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()
            payloadTemplateMgr = PayloadTemplateManager(bpmEnvironment)
            if payloadTemplateMgr.loggedIn == True:
                payloadTemplateMgr.generateTemplates(bpmEnvironment)
                payloadTemplateMgr.printDataTypes(_indentOutput)
    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    generatePayloadTemplates(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
