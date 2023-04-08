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


    #---------------------
    # tasks
    # tasks = [ts_test]
    tasks = [ bpmTask.SequenceOfBpmTasks ]
