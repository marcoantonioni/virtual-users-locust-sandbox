import bawsys.commandLineManager as clpm
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
import requests, json, sys, logging, os
from base64 import b64encode
from bawsys import bawUtils as bawUtils 

from contextlib import redirect_stdout

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
        self.dtSchemaTypeTemplate = ''

    def getClassRefKey(self):
        return self.dtId+"/"+self.dtSnapId

    def buildClassRefKey(self, pdtId, pdtSnapId):
        return pdtId+"/"+pdtSnapId


    #================================
    # Schema

    def buildJsonArributeForSchema(self, pName: str, pClass: str, pIsArr: bool, referencedTypeName: str):
        attrType = "object"
        if pClass == "String":
            attrType = "string"
            
        if pClass == "Boolean":
            attrType = "boolean"
            
        if pClass == "Integer":
            attrType = "integer"

        if pClass == "Decimal":
            attrType = "number"
            
        if pClass == "Date":
            attrType = "string"

        if pClass == "Time":
            attrType = "string"

        if referencedTypeName != None:
            attrType = "object"

        if pIsArr == True:
            return '"'+pName+'": {"type": "array", "items": { "type": "'+attrType+'" }}'
        return '"'+pName+'": {"type": "'+attrType+'"}'

    def builTemplateForSchema(self, dataTypeTemplatesByClassRef: dict):
        #self.templateBuilt = True
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

            if referencedTypeName != None:
                referencedTypes.append('\''+pName+'\' of type '+referencedTypeName)
            attrib = self.buildJsonArributeForSchema(pName, pClass, pIsArr, referencedTypeName)
            attribs += attrib
            if (tot > 1):
                attribs += ", "
            idxTemplate = idxTemplate + 1
            tot = tot -1
        refs = "#==========================\n# Create Json schema for "+self.dtName+" json type\n" 
        for r in referencedTypes:
            refs += '# '+r
            refs += "\n"
        self.dtSchemaTypeTemplate = refs+'jschema_'+self.dtName+'= {\n    "name": "'+self.dtName+'",\n    "properties": {\n        '+attribs.replace("}, ","},\n        ")+'},\n    "additionalProperties": False\n}'

    #================================



    def buildJsonArribute(self, pName: str, pClass: str, pIsArr: bool, referencedTypeName: str):
        templatePayload = ""

        attrVal = '""'
        if pClass == "Boolean":
            attrVal = "False"
            
        if pClass == "Integer":
            attrVal = "0"

        if pClass == "Decimal":
            attrVal = "0.0"
            
        if pClass == "Date":
            attrVal = "None"

        if pClass == "Time":
            attrVal = "None"

        if referencedTypeName != None:
            attrVal = '{}'

        if pIsArr == True:
            templatePayload = '"'+pName+'": []'
        else:
            templatePayload = '"'+pName+'": '+attrVal
        return templatePayload

    def builTemplate(self, dataTypeTemplatesByClassRef: dict):
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
            dtTemplate.builTemplate(self.dataTypeTemplatesByClassRef)

    def buildTypeTemplateForSchema(self):
        for dtName in self.dataTypeTemplates.keys():
            dtTemplate : DataTypeTemplate = self.dataTypeTemplates[dtName]
            dtTemplate.builTemplateForSchema(self.dataTypeTemplatesByClassRef)

    def generateTemplates(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        # load all data types, add in allDataTypes dict using boId+boSnapId key
        self.getModel(bpmEnvironment)
        # build data type template
        self.buildTypeTemplate()
        self.buildTypeTemplateForSchema()

    def printDataTypes(self):
        indent = False
        print("# ==================================")
        print("# Python code for data model objects\n# Application ["+self.appName+"] Acronym ["+self.appAcronym+"] Snapshot ["+self.appSnapName+"] Tip ["+str(self.useTip)+"]")
        print("# ==================================\n")
        for dtName in self.dataTypeTemplates.keys():
            dtTemplate : DataTypeTemplate = self.dataTypeTemplates[dtName]
            payloadTemplate = dtTemplate.dtTypeTemplate            
            print(payloadTemplate+"\n\n")

    def printSchemaDataTypes(self):
        indent = False
        print("# ==================================")
        print("# Python code for JSON schema data model objects\n# Application ["+self.appName+"] Acronym ["+self.appAcronym+"] Snapshot ["+self.appSnapName+"] Tip ["+str(self.useTip)+"]")
        print("# ==================================\n")
        print("import warlock, json\n")
        for dtName in self.dataTypeTemplates.keys():
            dtTemplate : DataTypeTemplate = self.dataTypeTemplates[dtName]
            payloadTemplate = dtTemplate.dtSchemaTypeTemplate            
            print(payloadTemplate+"\n")
            print("# ----------------------------------")
            print("# Class definition for "+dtName+"\n# usage samples: youVar = "+dtName+"(), yourVar = "+dtName+"( {...} )")
            print(dtName+" = warlock.model_factory(jschema_"+dtName+")\n\n")

def writePayloadManagerTemplate(_outputPayloadManager):
    templateName = "./bawsys/template-payload-manager.yp"

    f1 = open(_outputPayloadManager, 'a+')
    f2 = open(templateName, 'r')
 
    # appending the contents of the second file to the first file
    f1.write(f2.read())
    f1.close()
    f2.close()

def generatePayloadTemplates(argv):

    ok = False
    if argv != None:
        bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:o:a", ["environment=", "output=", "autoname="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _outputPayloadManager = cmdLineMgr.getParam("o", "output")
            _outputAutoName = cmdLineMgr.getParam("a", "autoname")
            
            if _outputPayloadManager == None:
                _outputPayloadManager = ""
            else:
                if os.path.isdir(_outputPayloadManager):  
                    _outputAutoName = True 
                elif os.path.isfile(_outputPayloadManager):
                    _outputAutoName = False
                elif os.path.exists(_outputPayloadManager) == False:
                    _outputAutoName = True
                else:
                    print("Wrong combination for output and autonaming")
                    sys.exit()                

            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()
            payloadTemplateMgr = PayloadTemplateManager(bpmEnvironment)
            if payloadTemplateMgr.loggedIn == True:
                print("Working...")
                payloadTemplateMgr.generateTemplates(bpmEnvironment)
                redirectOutput = False
                outName = "stdout"
                _outputNameSchema = "stdout"
                if len(_outputPayloadManager) > 0:
                    redirectOutput = True
                    if _outputAutoName == True:
                        tip = ""
                        if payloadTemplateMgr.useTip == True:
                            tip = "-tip"
                        if payloadTemplateMgr.appSnapName == None or payloadTemplateMgr.appSnapName == "":
                            tip = "tip"
                        fName = "payloadManager-"+payloadTemplateMgr.appName+"-"+payloadTemplateMgr.appAcronym+"-"+payloadTemplateMgr.appSnapName+tip
                        fName = fName.replace(".","-")
                        fNameSchema = fName+"-JsonSchema"
                        if _outputPayloadManager[-1] == "/":
                            _outputPayloadManager = _outputPayloadManager[:-1]
                        else:
                            if _outputPayloadManager[-1] == "\\":
                                _outputPayloadManager = _outputPayloadManager[:-1]
                        _outputNameSchema = _outputPayloadManager+"/"+fNameSchema+".py"
                        _outputPayloadManager = _outputPayloadManager+"/"+fName+".py"                        
                    outName = _outputPayloadManager
                print("Generating Python code for payload manager to "+outName+"\n# Application ["+payloadTemplateMgr.appName+"] Acronym ["+payloadTemplateMgr.appAcronym+"] Snapshot ["+payloadTemplateMgr.appSnapName+"] Tip ["+payloadTemplateMgr.appSnapTip+"]")
                if redirectOutput:
                    print("Ouput PayloadManager to file ", _outputPayloadManager)
                    with open(_outputPayloadManager, 'w') as f:
                        with redirect_stdout(f):
                            payloadTemplateMgr.printDataTypes()
                        f.close()
                    writePayloadManagerTemplate(_outputPayloadManager)

                    print("Ouput JSON Schema to file ", _outputNameSchema)
                    with open(_outputNameSchema, 'w') as fs:
                        with redirect_stdout(fs):
                            payloadTemplateMgr.printSchemaDataTypes()
                        fs.close()
                else:
                    payloadTemplateMgr.printDataTypes()
                    payloadTemplateMgr.printSchemaDataTypes()
    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    generatePayloadTemplates(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
