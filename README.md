# virtual-users-locust-sandbox

Sandbox per struttura progetto finale


```
# moduli installati
pip install locust
pip install jproperties

# 8 utenti 1/8
locust --config=./configurations/baw-vu-cfg-1.conf

# 2 utenti 9/10
locust --config=./configurations/baw-vu-cfg-2.conf

# traditional
locust --config=./configurations/baw-vu-cfg-1-traditional.conf


# 1 utente
locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 1 --spawn-rate 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# 10 utenti
locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 10 --spawn-rate 5 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# 2 utenti
locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 2 --spawn-rate 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds-user9-10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# creazione istanze
python ./createProcessInstance.py  -e ./configurations/env1.properties -i 10
python ./createProcessInstance.py  -e ./configurations/env1-traditional.properties -i 10

# terminazione istanze
python ./terminateProcessBulk.py -e ./configurations/env1.properties
python ./terminateProcessBulk.py  -e ./configurations/env1-traditional.properties

# cancellazione istanze
python ./deleteProcessBulk.py -e ./configurations/env1.properties -t true
python ./deleteProcessBulk.py  -e ./configurations/env1-traditional.properties -t true

# generazione template modello dati
python ./generatePayloadTemplates.py -e ./configurations/env1.properties -i true
python ./generatePayloadTemplates.py -e ./configurations/env1-traditional.properties -i true

# creazione utenze e gruppi ldap
python generateLDIFForVirtualUsers.py -c ./configurations/ldif4vu-cfg1.properties -l ./configurations/vux-cfg1.ldif -u ./configurations/creds-cfg1.csv

# onboard utenze in IAM
python ./iamOnboardUsers.py -e ./configurations/env1.properties -d vuxdomain -f ./configurations/creds-cfg1.csv


# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

# https://www.ibm.com/docs/en/bpm/8.6.0?topic=SSFPJS_8.6.0/com.ibm.wbpm.bpc.doc/topics/rrestapi_authtasks.htm

# https://www.ibm.com/docs/en/baw/22.x?topic=server-process-federation-rest-apis


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




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------




#---------------------------------------------------------------------------------






```

