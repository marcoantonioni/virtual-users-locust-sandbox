import bawsys.commandLineManager as clpm
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
from bawsys import templateManager as templMgr
import requests, json, sys, logging, os
from base64 import b64encode
from bawsys import bawUtils as bawUtils 

from contextlib import redirect_stdout

#----------------------------------

def generateOutputFileNames(payloadTemplateMgr: templMgr.PayloadTemplateManager, outPath: str):
    outNames = {}

    tip = ""
    if payloadTemplateMgr.useTip == True:
        tip = "_tip"
    if payloadTemplateMgr.appSnapName == None or payloadTemplateMgr.appSnapName == "":
        tip = "tip"
    fName = "payloadManager_"+payloadTemplateMgr.appName+"_"+payloadTemplateMgr.appAcronym+"_"+payloadTemplateMgr.appSnapName+tip
    fName = fName.replace(".","_")
    fNameDataModel = fName+"_DataModel"
    fNameSchema = fName+"_JsonSchema"
    if outPath[-1] == "/":
        outPath = outPath[:-1]
    else:
        if outPath[-1] == "\\":
            outPath = outPath[:-1]
    outNames["_outputNameSchema"] = outPath+"/"+fNameSchema+".py"
    outNames["_outputNameDataModel"] = outPath+"/"+fNameDataModel+".py"
    outNames["_outputPayloadManager"] = outPath+"/"+fName+".py"   

    return outNames

def writePayloadManagerTemplate(payloadTemplateMgr, _outputPayloadManager, _outputNameDataModel):
    templateName = "./bawsys/template-payload-manager.yp"

    f1 = open(_outputPayloadManager, 'w')
    f2 = open(templateName, 'r')
 
    f1.write("# ==================================\n")
    f1.write("# Python code for payload manager\n# Application ["+payloadTemplateMgr.appName+"] Acronym ["+payloadTemplateMgr.appAcronym+"] Snapshot ["+payloadTemplateMgr.appSnapName+"] Tip ["+payloadTemplateMgr.appSnapTip+"]\n")
    f1.write("# Application data model generated in file: "+_outputNameDataModel+"\n")
    f1.write("# ==================================\n\n")

    # appending the contents of the second file to the first file
    f1.write(f2.read())
    f1.close()
    f2.close()

def filesExists(fileNames):
    for f in fileNames:
        if os.path.exists(f):
            return True
    return False

def generatePayloadTemplates(argv):

    ok = False
    if argv != None:
        bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:o:af", ["environment=", "output=", "autoname=", "force="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _outputPayloadManager = cmdLineMgr.getParam("o", "output")
            _outputAutoName = cmdLineMgr.getParam("a", "autoname")
            _forceOverwrite = cmdLineMgr.getParam("f", "force")
            
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
            payloadTemplateMgr = templMgr.PayloadTemplateManager(bpmEnvironment)
            if payloadTemplateMgr.loggedIn == True:
                print("Working...")
                payloadTemplateMgr.generateTemplates(bpmEnvironment)

                redirectOutput = False
                outName = "stdout"
                _outputNameSchema = "stdout"
                _outputNameDataModel = "stdout"
                if len(_outputPayloadManager) > 0:
                    redirectOutput = True
                    if _outputAutoName == True:
                        outNames = generateOutputFileNames(payloadTemplateMgr, _outputPayloadManager)
                        _outputPayloadManager = outNames["_outputPayloadManager"] 
                        _outputNameSchema = outNames["_outputNameSchema"]
                        _outputNameDataModel = outNames["_outputNameDataModel"]

                    outName = _outputPayloadManager
                print("Generating Python code for payload manager to "+outName+"\n# Application ["+payloadTemplateMgr.appName+"] Acronym ["+payloadTemplateMgr.appAcronym+"] Snapshot ["+payloadTemplateMgr.appSnapName+"] Tip ["+payloadTemplateMgr.appSnapTip+"]")
                if redirectOutput:
                    okToWrite = True
                    if _forceOverwrite == None:
                        if filesExists([_outputNameDataModel, _outputPayloadManager, _outputNameSchema]):
                            print("Files exixts, use -f to force overwrite")
                            sys.exit()

                    if okToWrite:
                        print("Ouput DataModel to file ", _outputNameDataModel)
                        with open(_outputNameDataModel, 'w') as f:
                            with redirect_stdout(f):
                                payloadTemplateMgr.printDataTypes()
                            f.close()

                        print("Ouput PayloadManager to file ", _outputPayloadManager)
                        writePayloadManagerTemplate(payloadTemplateMgr, _outputPayloadManager, _outputNameDataModel)

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
