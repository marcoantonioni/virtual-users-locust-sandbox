import requests, json
import loadEnvironment as bpmEnv

requests.packages.urllib3.disable_warnings() 

class BpmExposedProcessInfo:
    def __init__(self, appName, appAcronym, processName, appId, appBpdId):
        self.appName = appName
        self.appAcronym = appAcronym
        self.processName = processName
        self.appId = appId
        self.appBpdId = appBpdId

    def getAppName(self):
        return self.appName
    
    def getAppAcronym(self):
        return self.appAcronym
    
    def getAppProcessName(self):
        return self.processName
    
    def getAppId(self):
        return self.appId
    
    def getAppBpdId(self):
        return self.appBpdId
    

def _bpmSearchProcessInstancesInfos(bpmEnvironment : bpmEnv.BpmEnvironment):
    exposedProcessInfo = dict()

    userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
    userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
    iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
    hostUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
    
    access_token : str = None
    cp4ba_token : str = None
    params : str = "grant_type=password&scope=openid&username="+userName+"&password="+userPassword
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    urlIdTk=iamUrl+"/idprovider/v1/auth/identitytoken"
    response = requests.post(url=urlIdTk, data=params, headers=my_headers, verify=False)
    if response.status_code == 200:
        access_token = response.json()["access_token"]
    if access_token != None:
        cp4ba_token : str = None
        my_headers = {'username': userName, 'iam-token': access_token }
        response = requests.get(url=hostUrl+"/v1/preauth/validateAuth", headers=my_headers, verify=False)
        if response.status_code == 200:
            cp4ba_token = response.json()["accessToken"]
            authValue : str = "Bearer "+cp4ba_token
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': authValue }
            baseUri = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
            urlExposed = hostUrl+baseUri+"/rest/bpm/wle/v1/exposed/process?excludeProcessStartUrl=false"
            #print(urlExposed)
            #print(my_headers)
            response = requests.get(url=urlExposed, headers=my_headers, verify=False)
            if response.status_code == 200:
                # print(json.dumps(response.json(), indent = 2))
                data = response.json()["data"]
                exposedItemsList = data["exposedItemsList"]
                appProcName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
                appProcAcronym = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
                processNames = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_NAMES)
                appProcessNames = processNames.split(",")
                listOfProcessInfos = []
                for expIt in exposedItemsList:
                    if appProcName == expIt["processAppName"] and appProcAcronym == expIt["processAppAcronym"]:
                        # print(json.dumps(expIt, indent = 2))
                        processName = expIt["display"]
                        for pn in appProcessNames:
                            if pn == processName:                        
                              listOfProcessInfos.append( BpmExposedProcessInfo(appProcName, appProcAcronym, processName, expIt["processAppID"], expIt["itemID"]) )
                return listOfProcessInfos
            else:
                print(response.status_code)
                print(response.text)                
                
    return None


#----------------------------------
def main():
    bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
    bpmEnvironment.loadEnvironment("./configurations/env1.properties")
    bpmEnvironment.dumpValues()
    appInfos = _bpmSearchProcessInstancesInfos(bpmEnvironment)
    for ai in appInfos:
        print(ai.getAppName()+" "+ai.getAppAcronym()+" "+ai.getAppProcessName())

if __name__ == "__main__":
    main()

"""
searchExposedProcess () {
  # $1 = app name
  # $2 = app acronym
  # $3 = process name
  # $4 = creds
  local RESPONSE=$(curl -sk -u $4 -H "${CONTENT}" -H "${ACCEPT}"  ${BASE_HOST}/bas/rest/bpm/wle/v1/exposed/process?excludeProcessStartUrl=false)
  
  if [ "${DEBUG}" == "true" ]; then
    _dumpJsonData "searchExposedProcess" "${RESPONSE}"
  fi
  
  HTTP_STATUS=$(echo ${RESPONSE} | jq .status | sed 's/\"//g')
  if [ "${HTTP_STATUS}" == "200" ]; then
    local IDX=0
    while [ true ];
    do
      local RECORD=$(echo ${RESPONSE} | jq .data.exposedItemsList[${IDX}])
      if [ "${RECORD}" == "null" ]; then
        break
      fi
      IDX=$((IDX+1))
      local PAPPNAME=$(echo ${RECORD} | jq .processAppName | sed 's/\"//g')
      local PAPPACRO=$(echo ${RECORD} | jq .processAppAcronym | sed 's/\"//g')
      local PROCESSNAME=$(echo ${RECORD} | jq .display | sed 's/\"//g')
      if [ "${PAPPNAME}" == "$1" ]; then
        if [ "${PAPPACRO}" == "$2" ]; then
          if [ "${PROCESSNAME}" == "$3" ]; then        
            APPID=$(echo ${RECORD} | jq .processAppID | sed 's/\"//g')
            BPDID=$(echo ${RECORD} | jq .itemID | sed 's/\"//g')
            APP_URISUFFIX=$(echo ${RECORD} | jq .startURL | sed 's/\"//g')
            break
          fi
        fi
      fi
    done
  else
    local ERROR_MSG=$(echo ${RESPONSE} | jq .Data.errorMessage | sed 's/\"//g') 
    echo "ERROR: ${HTTP_STATUS} - ${ERROR_MSG}"  
  fi
}

"""