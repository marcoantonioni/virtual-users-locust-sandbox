# BAWVUT User Guide

To prepare a test scenario, you must complete the following steps:

1. Configure runtime sandbox
1. Configure virtual users
1. Deploy your application
1. Configure BPM Groups and Application Teams
1. Export application Data Model and Code Template for payload manager and assert manager.
1. Customize python code for payload and assert managers
1. Update run configuration with generated python file names
1. Run LOAD_TEST or UNIT_TEST scenario
1. Analyze the results


## 1. Configure runtime sandbox

To prepare a configuration file for BAWVUT, follow these steps:

---
### 1.1 - Create the "Virtual Users Session" file
---

This file should have a KEY=VALUE structure.
It must reference four other files: 'BAWVirtualUsersTool.py', 'env.properties', 'creds.csv', and 'TS.csv'.
The file extension should be '.conf'.
The file must be referenced as the value of the '--config' parameter for the 'locust' command.
Populate the "Virtual Users Session" file

#### Include the following keys and values:
---
**locustfile**
: Path to the 'BAWVirtualUsersTool.py' file.

**headless**
: Execution mode of the Locust tool (true or false).

**host**
: A reference URL (e.g., http://nowhere.net).

**only-summary**
: Type of final report produced by locust (true or false).

**users**
: Number of virtual users to start in the session.

**spawn-rate**
: Number of users started every second.

**run-time**
: Maximum time execution in minutes.

**loglevel**
: Log verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

**BAW_ENV**
: Path to the runtime environment configuration file.

**BAW_USERS**
: Path to the user credentials file.

**BAW_TASK_SUBJECTS**
: Path to the TaskSubjects configuration file.

**BAW_USER_TASK_SUBJECTS**
: Path to the configuration file for associating Users to TaskSubjects.

---
### 1.2 - Create the "Runtime Environment" file
---

This file should also have a KEY=VALUE structure.
It is referenced by the variable 
BAW_ENV
.
It contains dedicated sections with sets of 'key=values' statements.
Populate the "Runtime Environment" file


#### Include the following sections and keys:
---
Runtime environment values:

BAW_IAM_HOST
: Host name for CP4BA IAM access.

BAW_BASE_HOST
: Host name for BAW access.

BAW_BASE_URI_SERVER
: Used only if BAW_TASK_LIST_STRATEGY=STANDALONE.

BAW_DEPLOYMENT_MODE
: Deployment mode (TRADITIONAL, PAK_STANDALONE, PAK_FEDERATED).

BAW_TASK_LIST_STRATEGY
: Task list strategy (STANDALONE, FEDERATEDPORTAL).

---
Admin and power user credentials:

BAW_POWER_USER_NAME
: BAW administrator user id.

BAW_POWER_USER_PASSWORD
: Password for the BAW administrator user.

BAW_IAM_USER_NAME
: PAK administrator user id (not used for Traditional deployment).

BAW_IAM_USER_PASSWORD
: Password for the PAK administrator user.

---
Users configuration:

BAW_USERS_STRATEGY
: Virtual users uniqueness (UNIQUE, TWINS).

BAW_USERS_TYPE
: Future use (REAL, VUX_NUMBERED).

BAW_USER_ORDER_MODE
: Users login order (SORTED_FIFO, SORTED_LIFO, SORTED_RANDOM).

BAW_VU_THINK_TIME_MIN
: Virtual User think time for task commands.

BAW_VU_VERBOSE
: Log message mode for idle virtual user (false, true).

BAW_VU_IDLE_NOTIFY
: Log idle virtual user (false, true).

BAW_VU_IDLE_NOTIFY_AFTER_NUM_INTERACTIONS
: Logs idle virtual users after N iterations.

---
Application configuration:

BAW_PROCESS_APPLICATION_NAME
: Application name.

BAW_PROCESS_APPLICATION_ACRONYM
: Application acronym.

BAW_PROCESS_APPLICATION_SNAPSHOT_NAME
: Application snapshot name (empty if using TIP in dev env).

BAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP
: Tip mode in dev env (true, false).

---
Processes and actions configuration:

BAW_PROCESS_NAMES
: Comma-separated list of process names.

BAW_VU_ACTIONS
: Comma-separated list of actions (LOGIN, CLAIM, COMPLETE, GETDATA, SETDATA, RELEASE, CREATEPROCESS).

---
Run configuration:

BAW_RUN_MODE
: Run mode (LOAD_TEST, UNIT_TEST).

BAW_PAYLOAD_MANAGER
: Full pathname of python dynamically loaded module.

BAW_PROCESS_INSTANCES_MAX
: Max number of process instances created during the run.

---
Unit Test Scenario:

BAW_UNIT_TEST_MAX_DURATION
: Maximum duration in minutes.

BAW_UNIT_TEST_OUT_FILE_NAME
: Output data of complete instances to file.

BAW_UNIT_TEST_OUT_USE_DB
: Output data to SQLite db (false, true).

BAW_UNIT_TEST_OUT_SQLITEDB_NAME
: SQLite db file.

BAW_UNIT_TEST_RUN_ASSERTS_MANAGER
: Run assert manager at the end of unit test (false, true).

BAW_UNIT_TEST_ASSERTS_MANAGER
: Full pathname of python dynamically loaded module.

---
### 1.3 - Create the "Name Password Email" file
---

This file should have a CSV structure.
It is referenced by the variable 
BAW_USERS
.
Each row should contain three columns names (email value is optional):
- NAME
- PASSWORD 
- EMAIL

All users listed in this file must be present in the authentication domain configured for the runtime environment.

---
### 1.4 - Create the "Task Subjects" file
---

This file should have a CSV structure.
It is referenced by the variable 
BAW_TASK_SUBJECTS
.
It should contain two columns (both not empty): 
- TASK_SUBJECTS 
- SUBJECT_TEXT

---
### 1.5 - Create the "Users and Task Subjects" file:
---

This file should have a CSV structure.
It is referenced by the variable 
BAW_USER_TASK_SUBJECTS
.
It should contain two or more columns (TSN columns may be empty): 
- USER 
- TSN1
- TSNn...

---
After preparing all the configuration files, ensure that the paths in the "Virtual Users Session" file correctly reference the other files. Then, you can start your BAWVUT run session using the 'locust' command with the '--config' parameter pointing to the "Virtual Users Session" file.

---
## 2. Configure virtual users

To create a file in .ldif format use the command 'generateLDIFForVirtualUsers.py'.

example:
```
python generateLDIFForVirtualUsers.py -c ../virtual-users-locust-test-configs/configurations/ldif4vu-cfg1.properties -l ../virtual-users-locust-test-configs/configurations/vux-cfg1.ldif -u ../virtual-users-locust-test-configs/configurations/creds-cfg1.csv
```

Parameters '-c' and '-u' are the input files to the command, parameter '-l' defines the path of the file that will be generated. The generated file can then be used to configure an LDAP.

For CP4BA IDP/LDAP configuration see git repo [cp4ba-idp-ldap](https://github.com/marcoantonioni/cp4ba-idp-ldap)

## 3. Deploy your application

To deploy a BAW application in CP4BA production-like environment use the command '' from repository [virtual-users-locust-apps](https://github.com/marcoantonioni/virtual-users-locust-apps)

example:
```
TNS=cp4ba-demo
BAW_NAME=baw1
CR_CP4BA=icp4adeploy
PAKADMIN_USER=cp4admin
PAKADMIN_PASSWORD=dem0s
APPLICATION=../zips/VirtualUsersSandbox-0.3.11.zip

./install-application.sh -n ${TNS} -b ${BAW_NAME} -c ${CR_CP4BA} -u ${PAKADMIN_USER} -p ${PAKADMIN_PASSWORD} -a ${APPLICATION}
```

## 4. Configure BPM Groups and Application Teams

## 5. Export application Data Model and Code Template for payload manager and assert manager

## 6. Customize python code for payload and assert managers

## 7. Update run configuration with generated python file names

## 8. Run LOAD_TEST or UNIT_TEST scenario
