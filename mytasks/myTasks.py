# tasks

import logging, time, random
from mytasks import loadCredentials
from locust import task, tag, events, SequentialTaskSet
from locust.runners import MasterRunner
from json import JSONDecodeError

#-------------------------------------------
# BPM type

class BpmTask:
    id : str = None
    subject : str = None

    def __init__(self, id, subject):
        self.id = id
        self.subject = subject

    def getId(self):
        return self.id

    def getSubject(self):
        return self.subject
    
    pass

class BpmTaskList:
    count : int = 0
    bpmTasks : BpmTask = None

    def __init__(self, count, bpmTasks):
        self.count = count
        self.bpmTasks = bpmTasks

    def getCount(self):
        return self.count

    def getTasks(self):
        return self.bpmTasks
    
    pass

#-------------------------------------------
# bpm logic
# self = MyUser

def __buildTaskList(bpmData):
    # test
    bpmTask1 = BpmTask("1", "subject 1")
    bpmTask2 = BpmTask("2", "subject 2")
    bpmTask3 = BpmTask("3", "subject 3")
    bpmTaksItems = [bpmTask1, bpmTask2, bpmTask3]
    bpmTaskList = BpmTaskList(len(bpmTaksItems), bpmTaksItems)
    return bpmTaskList

def _listAvailableTasks(self):
    if self.loggedIn == True:
        logging.info("list available tasks, user %s", self.userCreds.getName())

        # query task list

        # test
        bpmData = ""

        return __buildTaskList(bpmData);
    pass

def _listClaimedTasks(self):
    if self.loggedIn == True:
        logging.info("list claimed tasks, user %s", self.userCreds.getName())
    pass

def _taskGetData(self, taskId):
    if self.loggedIn == True:
        logging.info("task get data, user %s, task %s", self.userCreds.getName(), taskId)
    pass

def _taskSetData(self, taskId, payload):
    if self.loggedIn == True:
        logging.info("task set data, user %s, task %s, payload %s", self.userCreds.getName(), taskId, payload)
    pass

def _taskComplete(self, taskId, payload):
    if self.loggedIn == True:
        logging.info("task complete, user %s, task %s, payload %s", self.userCreds.getName(), taskId, payload)

        # test
        with self.client.get("/test", catch_response=True) as response:
            # logging.info("status code: %s", response.status_code)
            if response.status_code == 200:
                try:
                    if response.json()["id"] != "id1":                        
                        response.failure("Did not get expected value in response")
                except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                except KeyError:
                        response.failure("Response did not contain expected key 'greeting'")


    pass

#-------------------------------------------
class SequenceOfBpmTasks(SequentialTaskSet):
    def login(self):
        if self.user.loggedIn == False:
            uName = "n/a"
            if self.user.userCreds != None:
                uName = self.user.userCreds.getName()
                self.user.loggedIn = True
                logging.info("*** login, user %s", uName)
        pass

    def claim(self):
        if self.user.loggedIn == True:
            taskList : BpmTaskList = _listAvailableTasks(self.user)

            # test
            idx : int = random.randint(0, taskList.getCount()-1)
            bpmTask : BpmTask = taskList.getTasks()[idx];
            taskInfo : str = "[" + bpmTask.getId() + " - " + bpmTask.getSubject()+"]"

            logging.info("claim, user %s, task %s", self.user.userCreds.getName(), taskInfo )
        pass

    def complete(self):
        if self.user.loggedIn == True:
            _listClaimedTasks(self.user)

            think : int = random.randint(self.user.min_think_time, self.user.max_think_time)
            logging.info("working on task, user %s", self.user.userCreds.getName())
            time.sleep( think )            
            
            _taskComplete(self.user, "1", "{}")
            logging.info("complete task, user %s", self.user.userCreds.getName())
        pass

    # you can still use the tasks attribute to specify a list of tasks
    tasks = [login, claim, complete]

#-------------------------------------------
# test events
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    logging.info("A BPM test is starting")

    # legge csv e valorizza array utenze
    loadCredentials.setupCredentials("./configurations/creds100.csv")
    pass

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    logging.info("A BPM test is ending")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner):
        logging.info("I'm on master node")
    else:
        logging.info("I'm on a worker or standalone node")