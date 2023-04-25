import logging, json
from json import JSONDecodeError

class RestResponseManager:
    contextName = None
    response = None
    userName = None
    bpmTask = None
    ignoreCodes = None
    js = None

    def __init__(self, contextName, response, userName, bpmTask, ignoreCodes):
        self.contextName = contextName
        self.response = response
        self.userName = userName
        self.bpmTask = bpmTask
        self.ignoreCodes = ignoreCodes
        self.js = {}
        self.isJsObj = False
        try:
            self.js = response.json()
            #print(json.dumps(self.js, indent=2))
            self.isJsObj = True
        except:
            logging.error("%s, status code [%s], error text [%s], empty/not-valid json content", contextName, response.status_code, response.text)

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug("%s status code: %s", contextName, response.status_code)
        if response.status_code >= 300:
            ignoreCode = False
            # ignore codes in list
            for rc in ignoreCodes:
                if response.status_code == rc:
                    ignoreCode = True
                    response.success()
            taskId = ""
            taskSubject = ""
            taskData = None
            if self.bpmTask != None:
                taskId = self.bpmTask.getId()
                taskSubject = self.bpmTask.getSubject()
                taskData = self.bpmTask.getTaskData()
            data = None
            bpmErrorMessage = self.response.text
            if self.isJsObj == True:
                try:
                    try:
                        data = self.js["Data"]
                        bpmErrorMessage = data["errorMessage"]
                    except KeyError:
                        pass

                    if ignoreCode == False:
                        logging.error("%s error, user %s, task %s, subject '%s', status %d, error %s", self.contextName, self.userName, taskId, taskSubject, self.response.status_code, bpmErrorMessage)
                        if taskData != None:
                            logging.error("%s error, user %s, task %s, payload %s", self.contextName, self.userName, taskId, json.dumps(taskData))

                except JSONDecodeError:
                    logging.error("%s error, user %s, task %s, subject '%s', response could not be decoded as JSON", self.contextName, self.userName, taskId, taskSubject)
                    self.response.failure("Response could not be decoded as JSON")
                except KeyError:
                    logging.error("%s error, user %s, task %s, subject '%s', response did not contain expected key 'Data', 'errorMessage'", self.contextName, self.userName, taskId, taskSubject)
                    self.response.failure("Response did not contain expected key 'Data', 'errorMessage'")

    def getJson(self):
        return self.js
    
    def getStatusCode(self):
        return self.response.status_code
    
    def getObject(self, key: str):
        try:
            if self.isJsObj == True:
                return self.js[key]
            else:
                return None
        except JSONDecodeError:
            logging.error("%s error, user %s, response could not be decoded as JSON", self.contextName, self.userName)
            self.response.failure("Response could not be decoded as JSON")
        except KeyError:
            logging.error("%s error, user %s, response did not contain expected key '%s'", self.contextName, self.userName, key)
            self.response.failure("Response did not contain expected key '"+key+"'")
        return None
    
