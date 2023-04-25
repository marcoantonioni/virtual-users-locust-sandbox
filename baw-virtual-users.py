# Entry point for BAW Virtual Users Tool

from locust import FastHttpUser, task, between, tag, events
from locust.runners import MasterRunner
from json import JSONDecodeError
import logging, sys, importlib

import mytasks.myTasks as bpmTask
import mytasks.processInstanceManager as bpmPIM

import bawsys.loadEnvironment as bpmEnv
import bawsys.loadUserTaskSubjects as bpmUTS
import bawsys.loadCredentials as bpmCreds
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import bawSystem as bawSys 

bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
bpmUserSubjects : bpmUTS.BpmUserSubjects =bpmUTS.BpmUserSubjects()
bpmExposedProcessManager : bpmExpProcs.BpmExposedProcessManager = bpmExpProcs.BpmExposedProcessManager()
bpmProcessInstanceManager : bpmPIM.BpmProcessInstanceManager = bpmPIM.BpmProcessInstanceManager()

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

    #----------------------------------------
    # user functions

    def _payload(self, subject, preExistPayload = None):
        return bpmDynamicModule.buildPayloadForSubject(subject, preExistPayload)

    def getEnvValue(self, key):
        return bpmEnvironment.getValue(key)

    def getEnvironment(self):
        return bpmEnvironment

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
            self.selectedUserActions[bpmEnv.BpmEnvironment.keyBAW_ACTION_LOGIN] = bpmEnv.BpmEnvironment.keyBAW_ACTION_ACTIVATED
            setOfActions = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_VU_ACTIONS)
            actions = setOfActions.split(",")
            for act in actions:
                action = act.strip().upper()
                if (action == bpmEnv.BpmEnvironment.keyBAW_ACTION_CLAIM) or action == bpmEnv.BpmEnvironment.keyBAW_ACTION_COMPLETE or action == bpmEnv.BpmEnvironment.keyBAW_ACTION_RELEASE or action == bpmEnv.BpmEnvironment.keyBAW_ACTION_GETDATA or action == bpmEnv.BpmEnvironment.keyBAW_ACTION_SETDATA or action == bpmEnv.BpmEnvironment.keyBAW_ACTION_CREATEPROCESS:
                    self.selectedUserActions[action] = bpmEnv.BpmEnvironment.keyBAW_ACTION_ACTIVATED

    def setIdleMode(self):
        strNotify : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_VU_IDLE_NOTIFY)
        strMaxInterctions : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_VU_IDLE_NOTIFY_AFTER_NUM_INTERACTIONS)
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
        self.host = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        self.min_think_time = int(bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_VU_THINK_TIME_MIN))
        self.max_think_time = int(bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_VU_THINK_TIME_MAX))
        self.setIdleMode()
        self.configureVirtualUserActions()
        self.runningTraditional = bawSys._isBawTraditional(bpmEnvironment)

        strVerbose : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_VU_VERBOSE)
        if strVerbose != None:
            self.verbose = strVerbose.lower() == "true"

        self.userCreds = bpmCreds.getNextUserCredentials()
        if self.userCreds != None:
            logging.debug("User %s is starting... ", self.userCreds.getName())
        else:
            # abort run
            logging.error("Error user %s not logged in... ", self.userCreds.getName())
            self.environment.runner.quit()

        return super().on_start()
    
    def on_stop(self):
        if self.userCreds != None:
            logging.debug("MyUser %s is stopping... ", self.userCreds.getName())
        return super().on_stop()

    #----------------------------------------
    # tasks definition    
    tasks = [ bpmTask.SequenceOfBpmTasks ]

#----------------------------------------
def import_module(name, package=None):
    absolute_name = importlib.util.resolve_name(name, package)
    try:
        return sys.modules[absolute_name]
    except KeyError:
        pass

    path = None
    if '.' in absolute_name:
        parent_name, _, child_name = absolute_name.rpartition('.')
        parent_module = import_module(parent_name)
        path = parent_module.__spec__.submodule_search_locations
    for finder in sys.meta_path:
        spec = finder.find_spec(absolute_name, path)
        if spec is not None:
            break
    else:
        msg = f'No module named {absolute_name!r}'
        raise ModuleNotFoundError(msg, name=absolute_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[absolute_name] = module
    spec.loader.exec_module(module)
    if path is not None:
        setattr(parent_module, child_name, module)
    return module

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
        bpmCreds.setupCredentials(_fullPathBawUsers, bpmEnvironment)

        # read user tasks dictionary
        taskSubjects = bpmUTS.setupTaskSubjects(_fullPathBawTaskSubjects)
        userTaskSubjects = bpmUTS.setupUserTaskSubjects(_fullPathBawUserTaskSubjects)
        userSubjectsDictionary = bpmUTS.createUserSubjectsDictionary(userTaskSubjects, taskSubjects)
        bpmUserSubjects.setDictionary(userSubjectsDictionary)
        bpmExposedProcessManager.LoadProcessInstancesInfos(bpmEnvironment)

        logging.debug("User Subjects Dictionary ", userSubjectsDictionary)
        logging.info("*** BAW EXPOSED PROCESSES ***")
        for key in bpmExposedProcessManager.getKeys():
            processInfo : bpmExpProcs.BpmExposedProcessInfo = bpmExposedProcessManager.getProcessInfos(key)
            if processInfo != None:
                logging.info("Process[%s] Application[%s] Acronym[%s]", processInfo.getAppProcessName(), processInfo.getAppName(), processInfo.getAppAcronym())
            else:
                logging.info("!!! object with key[%s] not found", key)
            
        logging.info("***********************")

        dynamicPLM : str = bpmEnvironment.getDynamicModuleFormatName()
        global bpmDynamicModule 
        bpmDynamicModule = import_module(dynamicPLM)
        
        bpmProcessInstanceManager.setupMaxInstances(bpmEnvironment)