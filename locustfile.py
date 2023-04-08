# locust --headless --autostart --only-summary --run-time 60s --users 3
# locust --headless --autostart --only-summary --run-time 60s --users 3 --generic
# locust --headless --autostart --only-summary --run-time 60s --users 3 --tags bpm generic
# locust --headless --autostart --only-summary --run-time 60s --users 300 --spawn-rate 30 --tags rest --host http://ts.locust.org:8080

# ok
# locust --headless --autostart --only-summary --run-time 60s --users 100 --spawn-rate 10 --host http://ts.locust.org:8080/

# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

import logging
import mytasks.myTasks as bpmTask
import mytasks.loadCredentials as creds

from locust import FastHttpUser, task, between, tag
from json import JSONDecodeError

class MyBpmUser(FastHttpUser):

    #---------------------
    # user vars
    min_think_time : int = 5
    max_think_time : int = 10
    
    userCreds : creds.UserCredentials = None
    loggedIn : bool = False
    authorizationBearerToken : str = None

    baseQDN : str = ".itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud"
    iamHost : str = "https://cp-console-cp4ba"+baseQDN
    cp4baHost : str = "https://cpd-cp4ba"+baseQDN

    #---------------------
    # user setup    
    
    min_time : float = 0.0
    max_time : float = 0.25
    wait_time = between(min_time, max_time)


    #---------------------
    # functions

    def context(self):
        return {"username": self.userCreds.getName()}

    # per ogni utente virtuale
    def on_start(self):
        
        self.userCreds = creds.getNextUserCredentials()
        if self.userCreds != None:
            logging.info("MyUser %s is starting... ", self.userCreds.getName())
        else:
            # abort run
            self.environment.runner.quit()

        return super().on_start()
    
    # per ogni utente virtuale
    def on_stop(self):
        if self.userCreds != None:
            logging.info("MyUser %s is stopping... ", self.userCreds.getName())
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
