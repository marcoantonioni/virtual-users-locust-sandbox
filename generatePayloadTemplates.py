import bulkProcessOperations
import bawsys.commandLineManager as clpm
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
import urllib, requests, json, sys

#----------------------------------

class PayloadTemplateManager:

    def __init__(self):
      self.cp4ba_token : str = None
      self.dataTypes = dict()
      self.parkedDataTypes = []
      self.parkedDataTypesId = dict()
      self.referencedClassRefId = dict()

    def buildJsonArributeTemplate(self, idxTemplate: int, pName: str, pClass: str, pIsArr: bool, pClassRef: str, pClasSnapId: str, referencedTypeName: str):
        templatePayload = ""
        templIdxVal = ""
        refTypeName = None
        if pClassRef != None:
            # complex type
            # ??? ricercare nome type
            if referencedTypeName != None:
                refTypeName = referencedTypeName
            else:
                refTypeName = pClassRef
                try:
                    refInfo = self.referencedClassRefId[pClassRef]
                    typeName = refInfo["typeName"]
                    if typeName != None:
                        refTypeName = typeName                    
                except KeyError:
                    pass
            templIdxVal = "@§§§"+str(idxTemplate)+"-type("+refTypeName+")§§§@"

        else:
            templIdxVal = "@§§§"+str(idxTemplate)+"§§§@"
            
        if pIsArr == True:
            templatePayload = pName+":['"+templIdxVal+"']"
        else:
            templatePayload = pName+":'"+templIdxVal+"'"

        return templatePayload

    def buildDataType(self, hostUrl, baseUri, dtName, dtId, snapId, appId, park: bool):

        authValue : str = "Bearer "+self.cp4ba_token
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        uriData = dtId+"?snapshotId="+snapId+"&processAppId="+appId
        urlDataType = hostUrl+uriBaseRest+"/businessobject/"+uriData

        response = requests.get(url=urlDataType, headers=my_headers, verify=False)
        referencesComplexTypes = False
        if response.status_code == 200:
            data = response.json()["data"]
            properties = data["properties"]
            idxTemplate = 1
            attribs = ""
            tot = len(properties)
            for prop in properties:
                pName = prop["name"]
                pClass = prop["typeClass"]
                pIsArr = prop["isArray"]

                isArr = "False"
                if pIsArr == True:
                    isArr = "True"
                pClassRef = None
                pClasSnapId = None
                try:
                    pClassRef = prop["typeClassRef"]
                    if pClassRef != None:
                        pClasSnapId = prop["typeClassSnapshotId"]
                except KeyError:
                    pass
                
                referencedTypeName = None
                if pClassRef != None:
                    referencesComplexTypes = True
                    dt = None
                    try:
                        dt = self.referencedClassRefId[pClassRef]
                        if dt != None:
                            referencedTypeName = dt["typeName"]                        
                    except KeyError:
                        pass
                    if referencedTypeName == None:
                        self.referencedClassRefId[pClassRef] = {'typeName': None, 'pClasSnapId': pClasSnapId } 

                attrib = self.buildJsonArributeTemplate(idxTemplate, pName, pClass, pIsArr, pClassRef, pClasSnapId, referencedTypeName)
                attribs += attrib
                if (tot > 1):
                    attribs += ","
                idxTemplate = idxTemplate + 1
                tot = tot -1
            if referencesComplexTypes == True and park == True:
                self.parkedDataTypes.append(dtName)
                self.parkedDataTypesId[dtName] = dtId                
            else:
                dtTypeTemplate = "{'varName':{"+attribs+"}}"
                self.dataTypes[dtName] = dtTypeTemplate 
                print(dtName+":\n"+dtTypeTemplate+"\n")

    def getModel(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
        bpmExposedProcessManager.LoadProcessInstancesInfos(bpmEnvironment)
        appId = bpmExposedProcessManager.getAppId()
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

        authValue : str = "Bearer "+self.cp4ba_token
        my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        urlAssetts = hostUrl+uriBaseRest+"/assets?processAppId="+appId

        response = requests.get(url=urlAssetts, headers=my_headers, verify=False)
        if response.status_code == 200:
            # print(json.dumps(response.json(), indent = 2))
            data = response.json()["data"]
            snapshotId = data["snapshotId"]
            dataTypesList = data["VariableType"]
            for dataType in dataTypesList:
                dtName = dataType["name"]
                dtId = dataType["poId"]
                self.buildDataType(hostUrl, baseUri, dtName, dtId, snapshotId, appId, True)

            while len(self.parkedDataTypes) > 0:
                dtName = self.parkedDataTypes.pop()
                dtId = self.parkedDataTypesId[dtName]
                print("Parked ", dtName)
                self.buildDataType(hostUrl, baseUri, dtName, dtId, snapshotId, appId, False)

    def generateTemplates(self, bpmEnvironment : bpmEnv.BpmEnvironment):

        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)

        if self.cp4ba_token == None:
            self.cp4ba_token = bawSys._loginZen(bpmEnvironment, iamUrl, hostUrl)
        if self.cp4ba_token != None:
            self.getModel(bpmEnvironment)

        pass

def generatePayloadTemplates(argv):

    ok = False
    if argv != None:
        bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:", ["environment="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()
            payloadTemplateMgr = PayloadTemplateManager()
            payloadTemplateMgr.generateTemplates(bpmEnvironment)
    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")

def main(argv):
    generatePayloadTemplates(argv)

if __name__ == "__main__":
    main(sys.argv[1:])

"""

#!/bin/bash
_me=$(basename "$0")

# RUN example: ./generatePayloadTemplates.sh -c "cp4admin:..." -e ./envs/environment.properties.ClaimCompileAndValidate

#--------------------------------------------------------
# read command line params
while getopts c:e: flag
do
    case "${flag}" in
        c) _C=${OPTARG};;
        e) _E=${OPTARG};;
    esac
done

export ENV_PROPS=${_E}
export CREDS=${_C}

#--------------------------------------------------------
# source params and common functions
source ./_commonValues.sh

#--------------------------------------------------------
# execute commands

function _buildJsonTemplatePaylod() {
  listOfMetadata=("$@")
  attrName="${listOfMetadata[0]}"
  attrTemplVal="@§§§${listOfMetadata[3]}§§§@"
  templatePayload=""
  if [ "${listOfMetadata[4]}" == "" ]; then
    # simple type
    if [ "${listOfMetadata[2]}" == "true" ]; then
      templatePayload="'${attrName}':['${attrTemplVal}']"
    else
      templatePayload="'${attrName}':'${attrTemplVal}'"
    fi
  else
    # complex type
    if [ "${listOfMetadata[2]}" == "true" ]; then
      templatePayload="'${attrName}':[{'${attrTemplVal}'}]"
    else
      templatePayload="'${attrName}':{'${attrTemplVal}'}"
    fi
 
  fi
  
  echo ${templatePayload}
}

function _showDataType() {
  DT_NAME=$1
  BO_ID=$2
  SNAP_ID=$3
  APP_ID=$4

  SUFFIX="${BO_ID}?snapshotId=${SNAP_ID}&processAppId=${APP_ID}"  
  FULL_QUERY="${BASE_HOST}/${BASE_BPM_REST}/businessobject/${SUFFIX}"
  RESPONSE_DT=$(curl -sk -u ${CREDS} -H "${CONTENT}" -H "${ACCEPT}" -X GET ${FULL_QUERY})
  echo "++++++++++++++++++++++++++++"
  DT_PROPERTIES=$(echo ${RESPONSE_DT} | jq .data.properties)
  NUM_PROPERTIES=$(echo ${RESPONSE_DT} | jq '.data.properties | length')
  DT_BUFFER=""
  for (( propIdx=0; propIdx<${NUM_PROPERTIES}; propIdx++ ))
  do
    DT_ATTRS=()
    PROPERTY=$(echo ${RESPONSE_DT} | jq .data.properties[${propIdx}])

    ATTR_NAME=$(echo ${PROPERTY} | jq .name | sed 's/\"//g')
    ATTR_TYPE=$(echo ${PROPERTY} | jq .typeClass | sed 's/\"//g')
    ATTR_IS_LIST=$(echo ${PROPERTY} | jq .isArray | sed 's/\"//g')
    ATTR_CLASSREF=$(echo ${PROPERTY} | jq .typeClassRef | sed 's/\"//g')

    DT_ATTRS+=($ATTR_NAME)
    DT_ATTRS+=($ATTR_TYPE)
    DT_ATTRS+=($ATTR_IS_LIST)
    DT_ATTRS+=($(($propIdx+1)))
    if [ "${ATTR_CLASSREF}" != "null" ]; then
      ATTR_CLASS_SNAPID=$(echo ${PROPERTY} | jq .typeClassSnapshotId | sed 's/\"//g')
      DT_ATTRS+=($ATTR_CLASSREF)
      DT_ATTRS+=($ATTR_CLASS_SNAPID)
    fi

    DT_BUFFER+=$(_buildJsonTemplatePaylod ${DT_ATTRS[@]})" "
  done
  
  FINAL_BUFFER=$(echo "{'varName':{"${DT_BUFFER}"}}" | sed 's/ /,/g' | sed 's/,}/}/g')
  echo "JSON Template payload for [${DT_NAME}]"
  echo ${FINAL_BUFFER} 
  echo "----------------------------"
}

function _generatePayloadTemplates() {
  _loadApplicationInfos

  FULL_QUERY="${BASE_HOST}/${BASE_BPM_REST}/assets?processAppId=${APPID}"
  RESPONSE=$(curl -sk -u ${CREDS} -H "${CONTENT}" -H "${ACCEPT}" -X GET ${FULL_QUERY})
  SNAP_ID=$(echo $RESPONSE | jq .data.snapshotId | sed 's/\"//g')
  NUM_DATA_TYPE=$(echo $RESPONSE | jq '.data.VariableType | length')
  for (( dtIdx=0; dtIdx<${NUM_DATA_TYPE}; dtIdx++ ))
  do
    DT=$(echo ${RESPONSE} | jq .data.VariableType[${dtIdx}])
    DT_NAME=$(echo ${DT} | jq .name | sed 's/\"//g')
    DT_POID=$(echo ${DT} | jq .poId | sed 's/\"//g')
    _showDataType ${DT_NAME} ${DT_POID} ${SNAP_ID} ${APPID}
  done
}

_generatePayloadTemplates

"""