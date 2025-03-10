# BAW Virtual Users Tool

**[WORK IN PROGRESS...]**

Last update: 2025-03-10

## Brief introduction
It is a tool written in Python language for simulating interactions between users and tasks of applications deployed in IBM Business Automation Workflow (both Traditional and CP4BA deployments).

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

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

## Context

Business Process Testing (BPT) validates end-to-end business workflows across multiple applications and systems, emphasizing the interconnectedness of these components. Crucial for identifying cross-functional impacts, BPT relies heavily on regression testing to detect unintended consequences from system changes. Given the complexity and time-intensive nature of testing diverse scenarios in long-running processes, automation is essential for effective BPT implementation, enabling efficient bug detection and ensuring system stability before production release.


## Test automation for business processes

The complexity in designing and executing end-to-end tests of a business process can lead the manager of the project to limit the preventive verification of the application functions with a consequent increase in the risks regarding the quality offered to the end user.
Due to the stateful nature of business process management applications, it is never trivial nor cheaper to deal with bug-fixing operations and subsequent migration of process instances from the original template to the new template which offers fixes or even new features.

In my experience gained in the previous role (business automation architect in the IBM Technology Expert Labs team), I have often supported customers also in this activity; each customer has independently chosen the products for generic functional tests, both open source and specific vendors. 
These have always been products that allow user interactions to be recorded via the browser and evaluate the outcome of the test based on the output presented in the browser.
This approach has its value but can only be thought of and implemented at the time of GUI stabilization.
It lacks the ability to evaluate everything that is internal to the business process or even what happens in the integration and choreography of activities outside the business process (intended in terms of values of process instance variables).
It is normal that generic products cannot in any way "look" inside the instance of the process nor apply logic of "assertions" on the internal data/variables of the process instance.

So it would be very useful to have a simple and flexible tool, easily adaptable to the functional business context and data model of each single process template and which allows you to make "assertions" on what is expected regarding the value of the process variables.

Here a list of the generic activities and costs necessary for business process testing.

The costs and time required are very often derived from:
- business solutions with frequent evolution of requirements and modification of user interfaces
- the process model becomes stable before the completion of the web interfaces, with generic tools (web interaction only) to perform an automated test you have to wait for the consolidation of the gui
- different frequency between user interface variation(+) and business process(-)
- redesigning tests that interact at the web browser level is often expensive, generic products are used to interact with the web browser
- complexity in collecting the final information relating to the outcome of a process instance

Some ideas on what is needed to carry out the activity

### Manual operations necessary for unit test setup
The costs and times required are very often derived from:
- definition of the snapshot on which to run the test
- cleaning of processes/tasks present on test environment (other versions of snapshots, previous runs, etc...)
- configuration of users and their profiling in the specific run time environment
- definition of the procedures and datasets that the user will have to follow/use for each use case (entire path of a process instance)
-- whoever defines the operating manual is usually not the developer, it's a second figure with knowledge of the application who will then have to somehow support the tester
- environment setup operations (among the recurring ones for each test and initial one-shot)

### Manual execution of unit tests
The costs and times required are very often derived from:
- it can be the developer if he has end-to-end visibility of the process, otherwise another suitably trained figure/role
- manual verification of results and comparison with expected data
- historicization of the test result
- difficulty of simultaneous use of the development environment between developers and testers caused by long times for manual execution of the tests
- dilated times between version development, manual tests and any feedback to the programmer for bug correction with subsequent reiteration of the tests

### Complexities, limitations and costs of manual activities
- communication between roles, obligation to produce updated documentation for each evolution
- use of common resources, runtime environment if not available a specific test environment
- continuous versioning and new version deployment in case of dedicated test environment, this involves exponential growth of the number of snapshots and increased frequency of environment updating activities
- execution and verification times

### Benefits of test automation
The benefits of adopting ad hoc tools
With a dedicated tool for IBM Business Automation Workflow you can:
- automate almost all of the manual test environment preparation operations
- run human interaction tests automatically
- perform automatic verification of the expected results
Redesigning the tests that interact at the TASK level is relatively simple and fast with the help of ad hoc tools for IBM Business Automation Workflow and allows to anticipate the test of the process logic compared to the test of the unique/gui specific logics.

### Benefits of Assertion Capability for Long-Running Processes

Assertions are crucial for verifying the correctness of long-running BPM processes. Here's why:

- <b>Verification of Asynchronous Operations</b>:
Long-running processes often involve asynchronous operations, making it challenging to determine when a process has completed and whether it has achieved the desired outcome. Assertions allow for the verification of the final state.

- <b>Data Integrity Checks</b>:
Assertions can verify that data has been correctly processed and stored at various stages of the process, ensuring data integrity.

- <b>Outcome Validation</b>:
They enable the validation of specific outcomes, such as the creation of a record in a database, the sending of an email, or the triggering of a downstream process.

- <b>Fault Tolerance Verification</b>:
Assertions can be used to verify that the process handles errors and exceptions correctly, ensuring fault tolerance.

- <b>Increased Test Reliability</b>:
Assertions provide a precise and automated way to verify process behavior, reducing the reliance on manual inspection and improving test reliability.

- <b>Monitoring of Process State</b>:
Assertions can be used to monitor the process state over time, and verify that the process has moved through the correct states.

- <b>Verification of business rules</b>:
Assertions can verify that the business rules within the process are being executed correctly.

- <b>Reduced manual testing</b>:
Automated assertions reduce the amount of manual testing required, saving time and resources.

### One of the possible solution is "BAW Virtual Users Tool" (BAWVUT)
With this open source tool you can:
- simulate the interaction with the process tasks present in the portal task list (list, claim, release, get data, update data, complete)
- start new process instances when exposed to a specific role
- define automatic verification of expected values (process instance variables)
- maintain the history of the runs and their outcome
- highlight which tests have failed and for what reason

### What if the same instrument dedicated to tests could also be used as a load generator?
With BAW VUT it is possible and with the only limitation of exclusion of GUI user interfaces,
these are not used because REST interactions directly use the API dedicated to TASKS.
This means that the measured performance will be related only to the server side business logic.
How ? Maintaining the same basic configuration and replacing the payload generator with, for example, the generation of random values always within the ranges allowed by the application.

### What can you achieve with this automation tool
- greater efficiency and productivity with reduction of test processing times and software correction
- reduction of costs inherent to the resources used
- improvement of the quality of the produced software

### How to evaluate this tool
- the tool is open source, released using MIT licenses (https://opensource.org/license/mit/)
- the tool is non-invasive, requires no installation of any kind on BAW servers, performs all its functions by simulating the end user from the outside and the system administrator for virtual users configurations
- the tool is based on Python 3 technology available on every operating system among the most commonly used ones
- the tool is also offered in Docker image format to simplify the client side setup operations
- has been designed and created to better support IBM customers and IBM partners who cannot use other tools for various reasons
- in the git repository there are demo applications and related pre-configurations that can be used to evaluate the tool with your minimum effort
- demo applications are available for both traditional IBM Business Automation Workflow environment (based on WAS-ND) and containerized environment (CP4BA)
- in addition to the main tool for executing the test/load, there are a series of support functions to simplify all setup and environment cleaning activities
- for the CP4BA containerized scenario there are simplification tools for LDAP deployment dedicated to virtual users and relative automatic IDP configuration
- the tool does not offer any mocking solutions for any services integrated by the processes being tested

### Tool description (to be completed...)
- technology (Python language, framework Locust)
- runtime (docker image, sources from git repo)
- limitations
- scalability in load scenarios
- description of git repo contents
- description of demo applications and their run configurations (test/load)
- how to configure and implement a test/load scenario
-- custom payload modules and assert managers
-- configuration of virtual users
-- assignment of virtual users to task subjects
- configuration needed for test scenarios
-- traditional scenery
-- containerized scenario
- run examples with docker image
- run examples with tool sources on client machine

Limits in thsi version: the tool does not manage the start of optional Activities

Note: In no way is this tool intended to replace the use of https://sdc-china.github.io/IDA-doc

## Companion repositories

This repository is accompanied by two other repos that contain the BAW applications (virtual-users-locust-apps) and the configurations used for the run tests (virtual-users-locust-test-configs).
Clone all 3 repositories to have the following structure on the file system:
<pre>
.
├── virtual-users-locust-sandbox
├── virtual-users-locust-apps
└── virtual-users-locust-test-configs
</pre>

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

## Docker image

[BAWVUT-Docker](./BAWVUT-Docker.md)

## Configuration files

[BAWVUT-Configuration](./docs/BAWVUT-Configuration.md)

## Development environment setup and configuration

Install Python modules 
```
pip install locust
pip install jproperties
pip install warlock
pip install jsonpath-ng

# optional
pip install sqlite-utils

# update to latest version
pip3 install -U --pre locust
```

## Run examples

### Run Load Test
Before run any scenario update configuration files for your runtime environment.

```
locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-1.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-starter.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-baw1.conf

locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-1-traditional.conf
```

### Run Unit Test
Before run any scenario update configuration files for your runtime environment.

```
locust --config=../virtual-users-locust-test-configs/configurations/baw-vu-cfg-ut1.conf
```

### Create process instances

```
python ./createProcessInstance.py -e ../virtual-users-locust-test-configs/configurations/env1.properties -i 10
```

### List process instances
```
python ./listProcessInstances.py -e ../virtual-users-locust-test-configs/configurations/env1.properties -s Active,Terminated,Completed,Failed -f 2025-03-01T00:00:00Z -t 2025-03-31T00:00:00Z
```

### Export process instance data

```
python ./exportProcessInstancesData.py -e ../virtual-users-locust-test-configs/configurations/env1.properties  -s Active,Terminated,Completed,Failed -f 2025-03-01T00:00:00Z -t 2025-03-31T00:00:00Z -n VUSClaimCompleteTwoRoles
```



### Tobe revised ...
```
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

# baw1-bai
python ./manageGroupsAndTeams.py -e ../virtual-users-locust-test-configs/configurations/env1-baw1-bai.properties -g ../virtual-users-locust-test-configs/configurations/groups-vu-baw1-bai.csv -t ../virtual-users-locust-test-configs/configurations/teams-vu-baw1-bai.csv -o add

sqlite-utils query --json-cols ./outputdata/unittest-scenario1-sqlite.db "SELECT * FROM BAW_UNIT_TEST_SCENARIO" | jq .
sqlite-utils query --json-cols ./outputdata/unittest-scenario1-sqlite.db "SELECT * FROM BAW_PROCESS_INSTANCES" | jq .
```

```
# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

# https://www.ibm.com/docs/en/bpm/8.6.0?topic=SSFPJS_8.6.0/com.ibm.wbpm.bpc.doc/topics/rrestapi_authtasks.htm

# https://www.ibm.com/docs/en/baw/22.x?topic=server-process-federation-rest-apis
```


## Preparazione struttura folder scenario
```
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
```

#### notes...
```
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

```
