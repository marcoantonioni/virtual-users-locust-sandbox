# virtual-users-locust-sandbox

Sandbox per struttura progetto finale


```
# moduli installati
pip install locust
pip install jproperties
pip install warlock
pip install jsonpath-ng

# optional
pip install sqlite-utils
```

Comandi vari
```

#---------------------------------
# Load test

cd /home/marco/locust/studio/bawvut/virtual-users-locust-sandbox

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-1.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-starter.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-baw1.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-1-traditional.conf


#---------------------------------
# Unit Test

cd /home/marco/locust/studio/virtual-users-locust-sandbox

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-ut1.conf


```



ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/configurations ./configurations
ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/outputdata ./outputdata

# test immagine ocp
sudo mkdir /bawvut
sudo ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/configurations /bawvut/configurations
sudo ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/outputdata /bawvut/outputdata

```
"""
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

```



Vecchi
```
locust --config=./configurations/baw-vu-cfg-1.conf

locust --config=./configurations/baw-vu-cfg-1-traditional.conf

#unit test
locust --config=./configurations/baw-vu-cfg-ut1.conf

# 1 utente
locust -f ./BAWVirtualUsersTool.py --headless --only-summary --run-time 60s --users 1 --spawn-rate 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# 10 utenti
locust -f ./BAWVirtualUsersTool.py --headless --only-summary --run-time 60s --users 10 --spawn-rate 5 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# 2 utenti
locust -f ./BAWVirtualUsersTool.py --headless --only-summary --run-time 60s --users 2 --spawn-rate 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds-user9-10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# creazione istanze
python ./createProcessInstance.py  -e ./configurations/env1.properties -i 10
python ./createProcessInstance.py  -e ./configurations/env1-traditional.properties -i 10

# lista istanze
python ./listProcessInstances.py -e ./configurations/env1.properties -s Active,Terminated,Completed,Failed -f 2023-04-01T00:00:00Z -t 2023-04-30T00:00:00Z
python ./listProcessInstances.py -e ./configurations/env1-traditional.properties -s Active,Terminated,Completed,Failed -f 2023-04-01T00:00:00Z -t 2023-04-30T00:00:00Z

# export dati istanza processo
python ./exportProcessInstancesData.py -e ./configurations/env1.properties -s Active,Terminated,Completed,Failed -f 2023-04-01T00:00:00Z -t 2023-04-30T00:00:00Z -n VUSClaimCompleteTwoRoles

python ./exportProcessInstancesData.py -e ./configurations/env1.properties -s Active,Terminated,Completed,Failed -f 2023-04-01T00:00:00Z -t 2023-04-30T00:00:00Z -n VUSClaimCompleteAuthorize


python ./exportProcessInstancesData.py -e ./configurations/test.properties -s Active,Terminated,Completed,Failed -f 2023-04-01T00:00:00Z -t 2023-04-30T00:00:00Z -n TestData

python ./exportProcessInstancesData.py -e ./configurations/test.properties -s Active,Terminated,Completed,Failed -f 2023-04-01T00:00:00Z -t 2023-04-30T00:00:00Z -n TestData -o ./outputdata/instances1.json


# terminazione istanze
python ./terminateProcessBulk.py -e ./configurations/env1.properties
python ./terminateProcessBulk.py  -e ./configurations/env1-traditional.properties

# cancellazione istanze
python ./deleteProcessBulk.py -e ./configurations/env1.properties -t true
python ./deleteProcessBulk.py  -e ./configurations/env1-traditional.properties -t true

# generazione template modello dati
python ./generateCodeFromTemplates.py -e ./configurations/env1.properties -o ./configurations
python ./generateCodeFromTemplates.py -e ./configurations/env1-traditional.properties -o ./configurations

python ./generateCodeFromTemplates.py -e ./configurations/env-ut1.properties -o ./configurations

python ./generateCodeFromTemplates.py -f -e ../virtual-users-locust-test-configs/configurations/env1-starter.properties -o ../virtual-users-locust-test-configs/configurations


# creazione utenze e gruppi ldap
python generateLDIFForVirtualUsers.py -c ./configurations/ldif4vu-cfg1.properties -l ./configurations/vux-cfg1.ldif -u ./configurations/creds-cfg1.csv

# onboard utenze in IAM
python ./iamOnboardUsers.py -e ./configurations/env1.properties -d vuxdomain -f ./configurations/creds-cfg1.csv

# gruppi e team bindings
python ./manageGroupsAndTeams.py -e ./configurations/env1.properties -g ./configurations/groups-vu-cfg1.csv -o add
python ./manageGroupsAndTeams.py -e ./configurations/env1.properties -g ./configurations/groups-vu-cfg1.csv -o remove

python ./manageGroupsAndTeams.py -e ./configurations/env1.properties -t ./configurations/teams-vu-cfg1.csv -o add
python ./manageGroupsAndTeams.py -e ./configurations/env1.properties -t ./configurations/teams-vu-cfg1.csv -o remove

python ./manageGroupsAndTeams.py -e ./configurations/env1.properties -g ./configurations/groups-vu-cfg1.csv -t ./configurations/teams-vu-cfg1.csv -o add

# unit test
python ./manageGroupsAndTeams.py -e ./configurations/env-ut1.properties -g ./configurations/groups-vu-cfg-ut1.csv -t ./configurations/teams-vu-cfg-ut1.csv -o add

sqlite-utils query --json-cols ./outputdata/unittest-scenario1-sqlite.db "SELECT * FROM BAW_UNIT_TEST_SCENARIO" | jq .
sqlite-utils query --json-cols ./outputdata/unittest-scenario1-sqlite.db "SELECT * FROM BAW_PROCESS_INSTANCES" | jq .

# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

# https://www.ibm.com/docs/en/bpm/8.6.0?topic=SSFPJS_8.6.0/com.ibm.wbpm.bpc.doc/topics/rrestapi_authtasks.htm

# https://www.ibm.com/docs/en/baw/22.x?topic=server-process-federation-rest-apis


#=================================================================================
# Preparazione struttura folder scenario

mkdir -p /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTip
mkdir -p /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTip/code
mkdir -p /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTip/outputdata

mkdir -p /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTipBis
mkdir -p /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTipBis/code
mkdir -p /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTipBis/outputdata

# tool folder
cd /home/marco/locust/studio/virtual-users-locust-sandbox/

python ./generateCodeFromTemplates.py -e /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTip/VirtualUsersSandbox-tip-env.properties -o /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTip/code

python ./generateCodeFromTemplates.py -e /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTipBis/VirtualUsersSandbox-tip-env.properties -o /home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTipBis/code

locust --config=/home/marco/locust/studio/BAWVUTScenarios/VirtualUsersSandboxTip/VirtualUsersSandbox-tip.conf


#=================================================================================
PFS Fedeated OpenAPI
https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud/pfs/rest/bpm/federated/openapi/index.html

#---------------------------------------------------------------------------------
Use this method to retrieve metadata for one or more federated IBM BPM systems. The attributes that are returned for each system depend on the system type.
curl -X 'GET' \
  'https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud/pfs/rest/bpm/federated/v1/systems' \
  -H 'accept: application/json'

{
  "federationResult": [
    {
      "restUrlPrefix": "https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud/bas/rest/bpm/wle",
      "systemID": "3216cb92-829d-49f4-a267-c2bc518347d0",
      "displayName": "3216cb92-829d-49f4-a267-c2bc518347d0",
      "systemType": "SYSTEM_TYPE_WLE",
      "id": "3216cb92-829d-49f4-a267-c2bc518347d0",
      "taskCompletionUrlPrefix": "https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud/bas/teamworks",
      "version": "8.6.4.22020",
      "indexRefreshInterval": 2000,
      "statusCode": "200"
    },
    {
      "restUrlPrefix": "https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud/bas/CaseManager/",
      "systemID": "04F9BF61-4B2C-4CA9-9C48-80769BF2F73B",
      "displayName": "04f9bf61-4b2c-4ca9-9c48-80769bf2f73b",
      "systemType": "SYSTEM_TYPE_CASE",
      "targetObjectStoreName": "TARGET",
      "id": "04f9bf61-4b2c-4ca9-9c48-80769bf2f73b",
      "version": "icm-22.0.2",
      "statusCode": "200"
    }
  ],
  "systems": [
    {
      "systemID": "3216cb92-829d-49f4-a267-c2bc518347d0",
      "systemType": "SYSTEM_TYPE_WLE",
      "version": "8.6.4.22020",
      "groupWorkItemsEnabled": false,
      "resources": [
        "tasks",
        "taskTemplates",
        "processes"
      ],
      "taskHistoryEnabled": false,
      "buildLevel": "BPM8600-20230215-170500",
      "substitutionEnabled": false,
      "workBasketsEnabled": false,
      "substitutionManagementRestrictedToAdministrators": false,
      "businessCategoriesEnabled": false,
      "taskSearchEnabled": false,
      "notificationWebMessagingEnabled": true,
      "taskListWebMessagingEnabled": true,
      "hostsTaskFilterService": true,
      "apiVersion": "1.0",
      "supports": null,
      "hostname": "icp4adeploy-bastudio-service.cp4ba.svc"
    },
    {
      "systemID": "04F9BF61-4B2C-4CA9-9C48-80769BF2F73B",
      "systemType": "SYSTEM_TYPE_CASE",
      "version": "icm-22.0.2",
      "isProduction": false,
      "cpeVersion": "content-engine-5.5.10-0-109",
      "targetObjectStoreName": "TARGET",
      "targetObjectStoreDisplayName": "TARGET"
    }
  ]
}
#---------------------------------------------------------------------------------


curl -X 'GET' \
  'https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud/pfs/rest/bpm/federated/v1/tasks?interaction=all&processAppName=VirtualUsersSandbox&offset=0&size=25&searchFilter=alfa%20beta%20gamma&filterByCurrentUser=false&calcStats=false&includeAllBusinessData=false' \
  -H 'accept: application/json'

#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------



```

