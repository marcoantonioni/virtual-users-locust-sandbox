# Entry point for BAW Virtual Users Tool

from locust import FastHttpUser, task, between, tag, events
from locust.runners import MasterRunner
from json import JSONDecodeError
import logging, sys
from datetime import datetime
import bawsys.bawTasks as bpmTask
import bawsys.processInstanceManager as bpmPIM

import bawsys.loadEnvironment as bawEnv
import bawsys.loadUserTaskSubjects as bpmUTS
import bawsys.loadCredentials as bpmCreds
import bawsys.exposedProcessManager as bpmExpProcs
import bawsys.processInstanceManager as bawPIM
import bawsys.bawUtils as bawUtils
from bawsys import bawSystem as bawSys
from bawsys import testScenarioManager as bawUnitTests 
from bawsys import testScenarioSqliteExport as sqliteExporter
from bawsys import testScenarioAssertManager as scenarioAsserts

import gevent, signal, time
from locust import events
from locust.runners import STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP, WorkerRunner

bpmEnvironment : bawEnv.BpmEnvironment = bawEnv.BpmEnvironment()
bpmUserSubjects : bpmUTS.BpmUserSubjects =bpmUTS.BpmUserSubjects()
bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
bpmProcessInstanceManager : bpmPIM.BpmProcessInstanceManager = bpmPIM.BpmProcessInstanceManager()
credsMgr : bpmCreds.CredentialsManager = bpmCreds.CredentialsManager()

class IBMBusinessAutomationWorkflowUser(FastHttpUser):

    #----------------------------------------
    # locust vars

    # to avoid --host in launch parmas, will be updated in 'on_start' method
    host = "https://www.ibm.com/products/business-automation-workflow"

    # locust wait time
    min_time : float = 0.0
    max_time : float = 0.25
    wait_time = between(min_time, max_time)

    #----------------------------------------
    # BAW user vars
    min_think_time : int = 0
    max_think_time : int = 1  
    loggedIn : bool = False
    runningTraditional = False
    cookieTraditional = None
    authorizationBearerToken : str = None    
    userCreds : bpmCreds.UserCredentials = None
    selectedUserActions = None
    idleNotify = False
    idleCounter = 0
    maxIdleLoops = 0
    verbose = False
    spawnedUsers = 0


    def __init__(self, environment):
        super().__init__(environment)

        self.tasks = []
        strRunMode = bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_RUN_MODE)
        if strRunMode == None or strRunMode == "" or strRunMode.lower() == "load_test":
            self.tasks = [ bpmTask.SequenceOfBpmTasks ]
        else:
            self.tasks = [ bpmTask.UnitTestScenario ]

        self.userCreds = credsMgr.getNextUserCredentials()
        if self.userCreds == None:
            logging.warning("Warning, credentials limit set to [%d], no more credentials available, next virtual users will not start.", IBMBusinessAutomationWorkflowUser.spawnedUsers)
            environment.reached_end = True
            environment.runner.quit()        
        else:
            IBMBusinessAutomationWorkflowUser.spawnedUsers += 1

    #----------------------------------------
    # user functions

    def getDynamicModule(self):
        return bpmDynamicModule

    def _payload(self, subject, preExistPayload = None):
        return bpmDynamicModule.buildPayloadForSubject(subject, preExistPayload)

    def getEnvValue(self, key):
        return bpmEnvironment.getValue(key)

    def getEnvironment(self):
        return bpmEnvironment
    
    def getExposedProcessManager(self):
        return bpmExposedProcessManager

    def context(self):
        return {"username": self.userCreds.getName()}

    def isSubjectForUser(self, taskSubjectText):
        found = False
        userId = self.userCreds.getName()
        dictionary = bpmUserSubjects.getDictionary()
        if dictionary != None:
            try:
                taskSubjects = dictionary[userId]
                for t in taskSubjects:
                    if bpmDynamicModule.isMatchingTaskSubject(taskSubjectText, t) != -1:
                        found = True
                        break
            except:
                # ignore, userId not in dictionary
                pass
        return found
    
    def getPIM(self):
        return bpmProcessInstanceManager
    
    def getEPM(self):
        return bpmExposedProcessManager
    
    def configureVirtualUserActions(self):
        if self.selectedUserActions == None:
            self.selectedUserActions = dict()
            self.selectedUserActions[bawEnv.BpmEnvironment.keyBAW_ACTION_LOGIN] = bawEnv.BpmEnvironment.keyBAW_ACTION_ACTIVATED
            setOfActions = bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_VU_ACTIONS)
            actions = setOfActions.split(",")
            for act in actions:
                action = act.strip().upper()
                if (action == bawEnv.BpmEnvironment.keyBAW_ACTION_REFRESH_TASK_LIST or action == bawEnv.BpmEnvironment.keyBAW_ACTION_CLAIM) or action == bawEnv.BpmEnvironment.keyBAW_ACTION_COMPLETE or action == bawEnv.BpmEnvironment.keyBAW_ACTION_RELEASE or action == bawEnv.BpmEnvironment.keyBAW_ACTION_GETDATA or action == bawEnv.BpmEnvironment.keyBAW_ACTION_SETDATA or action == bawEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS:
                    self.selectedUserActions[action] = bawEnv.BpmEnvironment.keyBAW_ACTION_ACTIVATED

    def setIdleMode(self):
        strNotify : str = bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_VU_IDLE_NOTIFY)
        strMaxInterctions : str = bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_VU_IDLE_NOTIFY_AFTER_NUM_INTERACTIONS)
        if strNotify != None:
            if strNotify.lower() == "true":
                self.idleNotify = True
                if strMaxInterctions != None:
                    try:
                        self.maxIdleLoops = int(strMaxInterctions)
                    except:
                        # abort run
                        logging.error("Error in IDLE parameters !")
                        self.environment.runner.quit()

    #----------------------------------------
    # for each virtual user

    def on_start(self):
        self.host = bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_BASE_HOST)
        self.min_think_time = int(bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_VU_THINK_TIME_MIN))
        self.max_think_time = int(bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_VU_THINK_TIME_MAX))
        self.setIdleMode()
        self.configureVirtualUserActions()
        self.runningTraditional = bawSys._isBawTraditional(bpmEnvironment)

        strVerbose : str = bpmEnvironment.getValue(bawEnv.BpmEnvironment.keyBAW_VU_VERBOSE)
        if strVerbose != None:
            self.verbose = strVerbose.lower() == "true"

        # TSM

        logging.debug("User %s is starting... ", self.userCreds.getName())

        return super().on_start()
    
    def on_stop(self):
        if self.userCreds != None:
            logging.debug("MyUser %s is stopping... ", self.userCreds.getName())
        return super().on_stop()

#----------------------------------------
# global events managers

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--BAW_ENV", type=str, env_var="LOCUST_BAW_ENV", include_in_web_ui=True, default="", help="ok")
    parser.add_argument("--BAW_USERS", type=str, env_var="LOCUST_BAW_USERS", include_in_web_ui=True, default="", help="ok")
    parser.add_argument("--BAW_TASK_SUBJECTS", type=str, env_var="LOCUST_BAW_TASK_SUBJECTS", include_in_web_ui=True, default="", help="ok")
    parser.add_argument("--BAW_USER_TASK_SUBJECTS", type=str, env_var="LOCUST_BAW_USER_TASK_SUBJECTS", include_in_web_ui=True, default="", help="ok")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logging.info("A BPM test is starting, BAW_ENV[%s] BAW_USERS[%s]", environment.parsed_options.BAW_ENV, environment.parsed_options.BAW_USERS)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logging.info("A BPM test is ending")

@events.init.add_listener
def on_locust_init(environment, **kwargs):

    try:
        if isinstance(environment.runner, MasterRunner):
            logging.debug("Running on master node")
        else:
            logging.debug("Running on a worker or standalone node")

        #----------------------------------------
        # setup environment and users
        _fullPathBawEnv = environment.parsed_options.BAW_ENV
        _fullPathBawUsers = environment.parsed_options.BAW_USERS
        _fullPathBawTaskSubjects = environment.parsed_options.BAW_TASK_SUBJECTS
        _fullPathBawUserTaskSubjects = environment.parsed_options.BAW_USER_TASK_SUBJECTS
        if _fullPathBawEnv == None or _fullPathBawUsers == None or _fullPathBawTaskSubjects == None or _fullPathBawUserTaskSubjects == None:
            logging.error("ERROR missed one or both mandatory environment variables, BAW_ENV[%s] BAW_USERS[%s]", _fullPathBawEnv, _fullPathBawUsers)
            environment.runner.quit()
        else:
            logging.debug("Setup BAW environment with BAW_ENV[%s] BAW_USERS[%s] BAW_TASK_SUBJECTS[%s] BAW_USER_TASK_SUBJECTS[%s]", _fullPathBawEnv, _fullPathBawUsers, _fullPathBawTaskSubjects, _fullPathBawUserTaskSubjects)

            # read properties
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()

            # read credentials
            credsMgr.setupCredentials(_fullPathBawUsers, bpmEnvironment)

            # read user tasks dictionary
            taskSubjects = bpmUTS.setupTaskSubjects(_fullPathBawTaskSubjects)
            userTaskSubjects = bpmUTS.setupUserTaskSubjects(_fullPathBawUserTaskSubjects)
            userSubjectsDictionary = bpmUTS.createUserSubjectsDictionary(userTaskSubjects, taskSubjects)
            bpmUserSubjects.setDictionary(userSubjectsDictionary)
            bpmExposedProcessManager.LoadProcessInstancesInfos(bpmEnvironment)

            logging.debug("User Subjects Dictionary ", userSubjectsDictionary)
            logging.info("*** BAW EXPOSED PROCESSES in Application [%s] Acronym [%s] Snapshot [%s] Tip [%s]", bpmExposedProcessManager.getAppName(), bpmExposedProcessManager.getAppAcronym(), bpmExposedProcessManager.getSnapshotName(), bpmExposedProcessManager.isTip())
            
            for key in bpmExposedProcessManager.getKeys():
                processInfo : bpmExpProcs.BpmExposedProcessInfo = bpmExposedProcessManager.getProcessInfos(key)
                if processInfo != None:
                    logging.info("Process [%s]", processInfo.getAppProcessName())
                else:
                    logging.info("!!! object with key[%s] not found", key)
                
            logging.info("***********************")

            dynamicPLM : str = bawUtils.getDynamicModuleFormatName(bpmEnvironment.getValue(bpmEnvironment.keyBAW_PAYLOAD_MANAGER))
            global bpmDynamicModule 
            bpmDynamicModule = bawUtils.import_module(dynamicPLM)
            
            bpmProcessInstanceManager.setupMaxInstances(bpmEnvironment)

            # only run this on master & standalone
            if not isinstance(environment.runner, WorkerRunner):
                gevent.spawn(unitTestInstancesExporter, environment)

    except BaseException as exception:
        logging.warning(f"Exception Name: {type(exception).__name__}")
        logging.warning(f"Exception Desc: {exception}")
        logging.error("Error in on_locust_init.")


@events.quitting.add_listener
def on_locust_quitting(environment, **kwargs):
    logging.debug("Quitting now...")
    return

@events.quit.add_listener
def on_locust_quit(**kwargs):
    logging.debug("Quit.")
    return

def unitTestInstancesExporter(environment):
    try:
        time.sleep(15)
        scenarioMgr : bawUnitTests.TestScenarioManager = bawUnitTests.TestScenarioManager.getInstance()
        # if running unit test
        if scenarioMgr != None:
            while not environment.runner.state in [STATE_STOPPING, STATE_STOPPED, STATE_CLEANUP]:
                if bpmProcessInstanceManager != None:
                    # export & save instances

                    finished = scenarioMgr.pollInstances(bpmProcessInstanceManager)
                    if finished:
                        completionCause = "all instances completed"
                        if scenarioMgr.timeLimitExceeded:
                            completionCause = "time limit exceeded and some instances may be in active state"
                        logging.info("Terminating unit test scenario, %s, stopping alla virtual users.", completionCause)
                        logging.info("Unit test scenario started at %s, ended at %s.", scenarioMgr.startedAtISO, scenarioMgr.endedAtISO)

                        # termina esecuzione virtual users
                        environment.runner.stop()

                        logging.info("Exporting data of test scenario, wait...")

                        listOfPids = bawUnitTests.TestScenarioManager.getInstance().listOfPids
                        # pim : bawPIM.BpmProcessInstanceManager = bawPIM.BpmProcessInstanceManager()
                        listOfInstances = bpmProcessInstanceManager.exportProcessInstancesDataByPid( bpmEnvironment=bpmEnvironment, listOfPids=listOfPids)
                        ouputName = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_OUT_FILE_NAME)
                        intTimeExceeded = 0
                        if scenarioMgr.timeLimitExceeded:
                            intTimeExceeded = 1 
                        assertsMgrName = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_ASSERTS_MANAGER)
                        if assertsMgrName == None:
                            assertsMgrName = ""
                        try:
                            bawUtils._writeOutScenarioInstances(listOfInstances, ouputName, scenarioMgr.startedAtISO, scenarioMgr.endedAtISO, len(listOfInstances), intTimeExceeded, assertsMgrName)
                            logging.info("Unit test data of [%d] process instances written to file '%s'", len(listOfInstances), ouputName)

                            useSqlite = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_OUT_USE_DB)
                            if useSqlite != None:
                                if useSqlite.lower() == "true":
                                    dbName = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_OUT_SQLITEDB_NAME)
                                    sqLiteExporter : sqliteExporter.TestScenarioSqliteExporter = sqliteExporter.TestScenarioSqliteExporter(dbName)
                                    sqLiteExporter.createDbAndSchema()
                                    sqLiteExporter.setScenarioInfos(scenarioMgr.startedAtISO, scenarioMgr.endedAtISO, len(listOfInstances), intTimeExceeded, assertsMgrName)
                                    sqLiteExporter.addScenario(listOfInstances)
                                    logging.info("Unit test data of [%d] process instances written to db '%s'", len(listOfInstances), dbName)

                                    strRunAssertsMagr = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_RUN_ASSERTS_MANAGER)
                                    if strRunAssertsMagr != None:
                                        if strRunAssertsMagr.lower() == "true":
                                            dynamicAM = bpmEnvironment.getValue(bpmEnvironment.keyBAW_UNIT_TEST_ASSERTS_MANAGER)
                                            if dynamicAM != None and dynamicAM != "":
                                                moduleName = bawUtils.getDynamicModuleFormatName(dynamicAM)
                                                bpmDynamicModuleAsserts = bawUtils.import_module(moduleName)
                                                assertsMgr : scenarioAsserts.ScenarioAssertsManager = scenarioAsserts.ScenarioAssertsManager(bpmEnvironment, bpmDynamicModuleAsserts)
                                                assertsMgr.executeAsserts(listOfInstances)

                        except BaseException as exception:
                            logging.warning(f"Exception Name: {type(exception).__name__}")
                            logging.warning(f"Exception Desc: {exception}")
                            logging.error("Error writing unit test process instance data")
                        logging.info("Unit test scenario terminated")
                        # elimina statistiche e termina esecuzione
                        environment.stats.clear_all()
                        environment.runner.quit()
                        return
                    
                time.sleep(5)
        else:
            logging.debug("Not unit testing")
    except:
        logging.error("Error running unitTestInstancesExporter")
    return

