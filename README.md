# BAW Virtual Users Tool

It is a tool written in Python language for simulating interactions between users and tasks of applications deployed in IBM Business Automation Workflow.

It is based on the open source tool Locust (https://locust.io)

The tool is designed to interact only with human tasks through the REST APIs made available by IBM BAW. The features allow you to request the list of tasks for a specific user, to claim a task, to release a previously claimed task to the team, to update the data of a task without completing it, to complete a task.

The tool also allows you to create new process instances with an optional startup payload.

It is possible to define a set of virtual users for each role defined in the process (TeamBindings). A virtual user can be associated with multiple roles. Each virtual user can be configured with its own access password.

The tool can interact with IBM BAW deployed in Traditional (WAS), Containerized (CP4BA), Federated (CP4BA, mix of BAW and WFPS) mode.

It can be used as a load generator for partial tests of applications and the underlying infrastructure. By partial test we mean that for example the workload normally generated for CSHS and Ajax calls is not activated because the tasks are only interacted with REST API calls, consequently the server is stressed less than in reality.

Furthermore, applications that use IME cannot be completed autonomously by the tool.

The tool is accompanied by an example application and a set of configurations that can be used as an example.

The tool can be used from the command line or as a containerized image. In case of a containerized image the configuration files must be previously inserted into a config map.

This tool is open source
```
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## Program structure

Description of most important python files.

### BAWVirtualUsersTool.py
The main module is <b>BAWVirtualUsersTool.py</b>, it is referenced by the '.conf' file used as the value of the '--config' parameter of the 'locust' program
```
locust --config=your-config-file
```
The module defines a series of methods for event management and a class <b>IBMBusinessAutomationWorkflowUser</b> that defines the data and operations of each single virtual user.

The initialization event management method runs the setup of a dynamic python module that is referenced by the variable <b>bpmDynamicModule</b>. The dynamic module implements the manager of the various payloads that are generated during the run for each task (update/completion) and for the creation of new process instances.
The python source file specific to the run is referenced by the variable <b>BAW_PAYLOAD_MANAGER</b> in '.properties' file in turn identified by the variable <b>BAW_ENV</b> in '.conf' file.

The 'unitTestInstancesExporter' method runs the export of the data of the processes that have been started for a run configured as a unit test. The data is inserted into a file in SQLite format and can be consulted with simple SQL queries.

### bawTasks.py
The module defines two classes, <b>SequenceOfBpmTasks(SequentialTaskSet)</b> and <b>UnitTestScenario(SequenceOfBpmTasks)</b>

The <b>SequenceOfBpmTasks</b> class extends SequentialTaskSet [from locust] and defines variables and methods for managing basic human task functionalities.

The <b>UnitTestScenario</b> class extends SequenceOfBpmTasks and defines the <b>bawCreateScenarioInstances</b> method for creating and cataloging process instances that will be the object of unit tests.

The methods defined by the <b>SequenceOfBpmTasks<b> class allow you to perform the functions of reading the available tasks (task list), reading and updating the data of a human task, executing the claim, releasing, completing a human task. Log in and create a new process instance.

The methods that generate a task data update and that start a new process instance make dynamic use of the payload manager defined by <b>bpmDynamicModule</b>.



WARNING: The following sections need to be updated and translated into English


## Development environment

```
# Python modules used
pip install locust
pip install jproperties
pip install warlock
pip install jsonpath-ng

# optional
pip install sqlite-utils
```

Commands (just as memo)
```

#---------------------------------
# Run Load Test

cd /home/marco/locust/studio/bawvut/virtual-users-locust-sandbox

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-1.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-starter.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-baw1.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-1-traditional.conf


#---------------------------------
# Run Unit Test

cd /home/marco/locust/studio/virtual-users-locust-sandbox

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-ut1.conf


```



ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/configurations ./configurations
ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/outputdata ./outputdata

# test docker image
sudo mkdir /bawvut
sudo ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/configurations /bawvut/configurations
sudo ln -s /home/marco/locust/studio/bawvut/virtual-users-locust-test-configs/outputdata /bawvut/outputdata




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

