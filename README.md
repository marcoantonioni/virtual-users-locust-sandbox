# virtual-users-locust-sandbox

Sandbox per struttura progetto finale

```

# 1 utente
locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 1 --spawn-rate 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# 10 utenti
locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 10 --spawn-rate 5 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# 2 utenti
locust -f ./baw-virtual-users.py --headless --only-summary --run-time 60s --users 2 --spawn-rate 1 --host http://ts.locust.org:8080/ --BAW_ENV ./configurations/env1.properties --BAW_USERS ./configurations/creds-user9-10.csv --BAW_TASK_SUBJECTS ./configurations/TS-TEST1.csv --BAW_USER_TASK_SUBJECTS ./configurations/US-TS-TEST1.csv

# https://github.com/locustio/locust/blob/master/examples/test_data_management.py
# https://github.com/locustio/locust/blob/master/examples/dynamic_user_credentials.py

# https://www.ibm.com/docs/en/bpm/8.6.0?topic=SSFPJS_8.6.0/com.ibm.wbpm.bpc.doc/topics/rrestapi_authtasks.htm

# moduli
pip install locust
pip install jproperties

BASE_HOST=https://cpd-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud

IAM_HOST=https://cp-console-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud


locust --headless --autostart --only-summary --run-time 5s --users 1 --host https://cp-console-cp4ba.itzroks-120000c7nk-ww08nj-6ccd7f378ae819553d37d5f2ee142bd6-0000.eu-gb.containers.appdomain.cloud






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

```

