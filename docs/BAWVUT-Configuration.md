# BAWVUT Configuration details

A run session is based on a set of configuration files.
A first file references the remaining ones and is used to start the session.
The first file <b>"Virtual Users Session"</b> (with extension '.conf') references 4 other files (extensions '.properties' and '.csv').

## The "Virtual Users Session" file 
This file has a KEY=VALUE structure.
It contains the following information:
<pre>
<b>locustfile</b> = the path to the 'BAWVirtualUsersTool.py' file that identifies the tool's starting point

<b>headless</b> = the Locust tool execution mode (values: true | false)

<b>host</b> = identifies a reference url (use a fake address: http://nowhere.net or other as desired)

<b>only-summary</b> = type of final report produced by locust (values: true | false)

<b>users</b> = number of virtual users that will be started in the session (e.g. 100) must be related to the users present in the runtime environment

<b>spawn-rate</b> = number of users started every second starting from the session start (e.g. 10)

<b>run-time</b> = maximum session execution time expressed in minutes (e.g. 10m)

<b>loglevel</b> = log verbosity level (values: DEBUG | INFO | WARNING | ERROR | CRITICAL)

<b>BAW_ENV</b> = the path to the configuration file of the environment (ex: ../virtual-users-locust-test-configs/configurations/env1.properties)

<b>BAW_USERS</b> = the path to the user credentials file (ex: ../virtual-users-locust-test-configs/configurations/creds-cfg1.csv)

<b>BAW_TASK_SUBJECTS</b> = the path to the TaskSubjects configuration file (ex: ../virtual-users-locust-test-configs/configurations/TS-TEST1.csv)

<b>BAW_USER_TASK_SUBJECTS</b> = the path to the configuration file for associating Users to TaskSubjects (ex: ../virtual-users-locust-test-configs/configurations/US-TS-TEST1.csv)
</pre>

## The "Runtime Environment" file 
This file has a KEY=VALUE structure.
It contains has dedicated sections each one with dedicated set of 'key=values' statements.

### Runtime environment values:
<pre>
<b>BAW_IAM_HOST</b> = host name for IAM access (ex: https://cp-console-cp4ba-demo.apps....)

<b>BAW_BASE_HOST</b> = host name for BAW access (ex: https://cpd-cp4ba-demo.apps....)

<b>BAW_BASE_URI_SERVER</b> = used only if BAW_TASK_LIST_STRATEGY=STANDALONE, empty if 'Traditional', for CP4BA BAStudio authoring the value is '/bas', if set must have a starting slash '/'

<b>BAW_DEPLOYMENT_MODE</b> = deployment mode (values: TRADITIONAL | PAK_STANDALONE | PAK_FEDERATED)

<b>BAW_TASK_LIST_STRATEGY</b> = task list strategi (values: STANDALONE | FEDERATEDPORTAL)
</pre>

### Admin and power user credentials:
<pre>
<b>BAW_POWER_USER_NAME</b> = BAW administrator user id (ex: cp4admin)

<b>BAW_POWER_USER_PASSWORD</b> = password

<b>BAW_IAM_USER_NAME</b> = PAK administrator user id (ex: cpadmin)

<b>BAW_IAM_USER_PASSWORD</b> = password
</pre>

### Users configuration
<pre>
<b>BAW_USERS_STRATEGY</b> = virtual users uniqueness (values: UNIQUE | TWINS) when TWINS multiple Locust runners can impersonate the same user id

<b>BAW_USERS_TYPE</b> = future use (REAL | VUX_NUMBERED)

<b>BAW_USER_ORDER_MODE</b> = users login order (SORTED_FIFO | SORTED_LIFO | SORTED_RANDOM)

<b>BAW_VU_THINK_TIME_MIN</b> = Virtual User think time for task complete, update, etc..., integer value in seconds

<b>BAW_VU_VERBOSE</b> = message mode for idle virtual user (false | true)

<b>BAW_VU_IDLE_NOTIFY</b> = log idle virtual user (false | true)

<b>BAW_VU_IDLE_NOTIFY_AFTER_NUM_INTERACTIONS</b> = log idle virtual users after N iterations (ex: 100)
</pre>

### Application configuration
<pre>
<b>BAW_PROCESS_APPLICATION_NAME</b> = application name (ex: VirtualUsersSandbox)

<b>BAW_PROCESS_APPLICATION_ACRONYM</b> = application acronym (ex: VUS)

<b>BAW_PROCESS_APPLICATION_SNAPSHOT_NAME</b> = application snapshot name (empty if using TIP in dev env)

<b>BAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP</b> = tip mode in dev env (values: true | false)
</pre>

### Processes and actions configuration
<pre>
<b>BAW_PROCESS_NAMES</b> = comma separated list of process names (ex: VUSClaimCompleteTwoRoles,VUSClaimCompleteAuthorize,ClaimCompileAndValidate)

<b>BAW_VU_ACTIONS</b> =CREATEPROCESS,TASK_LIST,CLAIM,GETDATA,SETDATA,COMPLETE,RELEASE

<i>BAW_VU_ACTIONS is a comma separated list of options (Login is always enabled): 
  value CLAIM: a unassign task
  value COMPLETE: complete a claimed task
  value GETDATA: get data values from claimd task
  value SETDATA: set data values to claimd task
  value RELEASE: release a claimed task to group
  value CREATEPROCESS: create a new process instance</i>
</pre>

### Run configuration
<pre>
<b>BAW_RUN_MODE</b> = run mode (values: LOAD_TEST | UNIT_TEST)

<b>BAW_PAYLOAD_MANAGER</b> = full pathname of python dynamically loaded module (ex: ../virtual-users-locust-test-configs/configurations/payloadManager-type1.py)

<b>BAW_PROCESS_INSTANCES_MAX</b> = max number of process instance created during the run, used by both run modes (ex: 100)
</pre>

### Unit Test Scenario
<pre>
<b>BAW_UNIT_TEST_MAX_DURATION</b> = in minutes (ex: 10)

<b>BAW_UNIT_TEST_OUT_FILE_NAME</b> = output data of complete instances to file (ex: ../virtual-users-locust-test-configs/outputdata/unittest-scenario1.json)

<b>BAW_UNIT_TEST_OUT_USE_DB</b> = output data of complete instances to SQLite db (values: false | true)

<b>BAW_UNIT_TEST_OUT_SQLITEDB_NAME</b> = output data of complete instances to SQLite db file (ex: ../virtual-users-locust-test-configs/outputdata/unittest-scenario1-sqlite.db)

<b>BAW_UNIT_TEST_RUN_ASSERTS_MANAGER</b> =run assert manager at the end of unit test (must use SQLlite db) (values: false | true)

<b>BAW_UNIT_TEST_ASSERTS_MANAGER</b> = full pathname of python dynamically loaded module (ex: ../virtual-users-locust-test-configs/configurations/assertsManager-type1.py)
</pre>

## The "Name Password Email" file 
This file has a CSV structure.

It contains users credentials and email. 
Each row contains the following information:
<pre>
<b>user-id, password, email</b>
</pre>
All users listed in this file must be present in the authentication domain configured for the runtime environment.

## The "Task Subjects" file 
This file has a CSV structure.

It is composed of two columns named <b>TASK_SUBJECTS</b> and <b>SUBJECT_TEXT</b>.

The TASK_SUBJECTS column identifies a unique key.
The SUBJECT_TEXT column defines the text of a task subject.
These values ​​guide the python module defined by <b>BAW_PAYLOAD_MANAGER</b> to generate the completion/update payload for a specific task.
<pre>
example:
  TASK_SUBJECTS,  SUBJECT_TEXT
  TS1,            "Compile Data [CCTR]"
  TS2,            "Validate Data [CCTR]"
  TS3,            "Compile Request [CCA]"
  TS4,            "Authorize Request [CCA]"
</pre>

## The "Users and Task Subjects" file 
This file has a CSV structure.

It is composed of two or more columns named <b>USER</b> and <b>TSN(n)</b>.

The USER column identifies a user id or a range of users when the authentication domain has a population of virtual users whose name is composed of a constant prefix and a progressive numeric postfix.
<pre>
example:
  USER,                   TSN1,   TSN2,   TSN3,   TSN4,  and more ...
  vuxuser1..vuxuser50,    TS1,    TS3
  vuxuser51..vuxuser90,   TS2,    TS4
  vuxuser91,              TS1
  vuxuser92,              TS2
</pre>
