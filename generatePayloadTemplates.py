

from bawsys import loadEnvironment as bawEnv

#----------------------------------

class PayloadTemplateManager:
    pass

def generatePayloadTemplates():
    bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()

    _fullPathBawEnv = "./configurations/env1.properties"
    bpmEnvironment.loadEnvironment(_fullPathBawEnv)
    bpmEnvironment.dumpValues()

    payloadTemplateMgr = PayloadTemplateManager()
    payloadTemplateMgr.generateTemplates(bpmEnvironment)

def main():
    generatePayloadTemplates()

if __name__ == "__main__":
    main()

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