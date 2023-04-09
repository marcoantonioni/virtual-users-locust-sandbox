
# ok
# locust --headless --only-summary --run-time 60s --users 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv
# locust --headless --only-summary --run-time 60s --users 100 --spawn-rate 25 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv

# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

import logging
import mytasks.myTasks as bpmTask
import mytasks.loadCredentials as bpmCreds
import mytasks.loadEnvironment as bpmEnv

from locust import FastHttpUser, task, between, tag, events
from locust.runners import MasterRunner
from json import JSONDecodeError

bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()

class IBMBusinessAutomationWorkflowUser(FastHttpUser):

    # to avoid --host in launch parmas, will be updated in 'on_start' method
    host = "https://www.ibm.com/products/business-automation-workflow"

    # locust wait time
    min_time : float = 0.0
    max_time : float = 0.25
    wait_time = between(min_time, max_time)

    #---------------------
    # BAW user vars
    min_think_time : int = 5
    max_think_time : int = 10    
    loggedIn : bool = False
    authorizationBearerToken : str = None    
    userCreds : bpmCreds.UserCredentials = None

    #---------------------
    # user functions

    def getEnvValue(self, key):
        return bpmEnvironment.getValue(key)

    def context(self):
        return {"username": self.userCreds.getName()}

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
    
    # for each virtual user
    def on_stop(self):
        if self.userCreds != None:
            logging.debug("MyUser %s is stopping... ", self.userCreds.getName())
        return super().on_stop()


    #*******************************************************
    #--------------------------------------------------
    # task senza peso assegnato   
    counter : int = 0
    counter2 : int = 0
 
    #@task
    def my_task(self):
        logging.info("executing my_task, counter=%d", self.counter)
        self.counter += 1
        if self.counter > 5:
            self.environment.runner.quit() 

    # task con peso assegnato    
    #@task
    def my_task_bis(self):
        logging.info("executing my_task_bis, counter2=%d", self.counter2)
        self.counter2 += 2


    #@task
    def ts_test(self):
        
        #response = self.client.get("/test");
        #logging.info("Response status code:", response.status_code)
        #logging.info("Response text:", response.text)
        
        with self.client.get("/test", catch_response=True) as response:
            #logging.info("status code: ", response.status_code)
            if response.status_code == 200:
                try:
                    if response.json()["id"] != "id1":                        
                        response.failure("Did not get expected value in response")
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'greeting'")
            
    #@task
    def all_tokens(self):
        baseQDN : str = ".itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud"
        iamHost : str = "https://cp-console-cp4ba"+baseQDN
        cp4baHost : str = "https://cpd-cp4ba"+baseQDN

        userName="user1"
        userPassword="passw0rd"
        access_token : str = bpmTask._accessToken(self, iamHost, userName, userPassword)
        logging.info("ACCESS TOKEN: %s", access_token)
        if access_token != None:
            cp4ba_token = bpmTask._cp4baToken(self, cp4baHost, userName, access_token)
            logging.info("CP4BA TOKEN: %s", cp4ba_token)
        self.environment.runner.quit() 

    #---------------------
    # tasks
    # tasks = [ts_test]
    # tasks = [all_tokens]
    tasks = [ bpmTask.SequenceOfBpmTasks ]



#-------------------------------------------
# test events

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

