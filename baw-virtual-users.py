
# ok
# locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv

# locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 10 --spawn-rate 5 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv

# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

import logging
from locust import FastHttpUser, task, between, tag, events
from locust.runners import MasterRunner
from json import JSONDecodeError

import mytasks.myTasks as bpmTask
import mytasks.loadCredentials as bpmCreds
import mytasks.loadEnvironment as bpmEnv

bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()

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
    min_think_time : int = 5
    max_think_time : int = 10    
    loggedIn : bool = False
    authorizationBearerToken : str = None    
    userCreds : bpmCreds.UserCredentials = None

    #----------------------------------------
    # user functions

    def getEnvValue(self, key):
        return bpmEnvironment.getValue(key)

    def context(self):
        return {"username": self.userCreds.getName()}

    #----------------------------------------
    # for each virtual user

    def on_start(self):
        self.host = host = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
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
# global events managers

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--BAW_ENV", type=str, env_var="LOCUST_BAW_ENV", include_in_web_ui=True, default="", help="ok")
    parser.add_argument("--BAW_USERS", type=str, env_var="LOCUST_BAW_USERS", include_in_web_ui=True, default="", help="ok")

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
    if _fullPathBawEnv == None or _fullPathBawUsers == None:
        logging.error("ERROR missed one or both mandatory environment variables, BAW_ENV[%s] BAW_USERS[%s]", _fullPathBawEnv, _fullPathBawUsers)
        environment.runner.quit()
    else:
        logging.debug("Setup BAW environment with BAW_ENV[%s] BAW_USERS[%s]", _fullPathBawEnv, _fullPathBawUsers)
        # read properties
        bpmEnvironment.loadEnvironment(_fullPathBawEnv)
        # read credentials
        bpmCreds.setupCredentials(_fullPathBawUsers)

