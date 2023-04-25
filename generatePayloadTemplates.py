import bulkProcessOperations
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

    def builTemplate(self, dataTypeTemplates: dict, dataTypeTemplatesByClassRef: dict):
        self.templateBuilt = True

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

            attrib = self.buildJsonArributeTemplate(idxTemplate, pName, pClass, pIsArr, pClassRef, pClasSnapId, referencedTypeName)
            attribs += attrib
            if (tot > 1):
                attribs += ","
            idxTemplate = idxTemplate + 1
            tot = tot -1

        self.dtTypeTemplate = '{"varName":{'+attribs+'}}'

class PayloadTemplateManager:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        self.dataTypeTemplates = dict()
        self.dataTypeTemplatesByClassRef = dict()

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

    def getModel(self):
        bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
        bpmExposedProcessManager.LoadProcessInstancesInfos(self.bpmEnvironment)
        appId = bpmExposedProcessManager.getAppId()
        hostUrl : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        urlAssetts = hostUrl+uriBaseRest+"/assets?processAppId="+appId

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

    def generateTemplates(self):
        # load all data types, add in allDataTypes dict using boId+boSnapId key
        self.getModel()
        # build data type template
        self.buildTypeTemplate()

    def printDataTypes(self, _indentOutput: str):
        indent = False
        if _indentOutput != None:
            indent = _indentOutput.lower() == "true"
        print()
        for dtName in self.dataTypeTemplates.keys():
            dtTemplate : DataTypeTemplate = self.dataTypeTemplates[dtName]
            payloadTemplate = None
            if indent == True:
                payloadTemplate = json.dumps( json.loads(dtTemplate.dtTypeTemplate), indent = 2)
            else:
                payloadTemplate = dtTemplate.dtTypeTemplate
            
            print("Data type: "+dtTemplate.dtName+"\n"+payloadTemplate+"\n")

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
                payloadTemplateMgr.generateTemplates()
                payloadTemplateMgr.printDataTypes(_indentOutput)
    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    generatePayloadTemplates(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
