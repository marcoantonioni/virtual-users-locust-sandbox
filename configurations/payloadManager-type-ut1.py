#==========================
# Create UTExample1Data json object
# 'data' of type UTExample1StartData
def newUTExample1Data():
    return {"data": {}, "vote": 0}


#==========================
# Create UTExample1StartData json object
def newUTExample1StartData():
    return {"counter": 0, "name": ""}


#=============================
# import section, add what you need
#=============================
import random, json

#=============================
# the function 'isMatchingTaskSubject' must be present in any payload manager
# it must return a Boolean, True when taskSubjectText match the subjext in a dictionary
# the default logic is: search as substring
# reimplement it as from your needs
#=============================

def isMatchingTaskSubject(taskSubjectText, subjectFromUserDictionary):
    return taskSubjectText.find(subjectFromUserDictionary) != -1

#=============================
# the function 'buildPayloadForSubject' must be present in any payload manager
# it must return a dict() object with keys
# jsonObject = your payload in json format
# thinkTime = your particular think thime for the subject in input; if the returned value is -1 the global think thime will be used
# reimplement it as from your needs
#=============================

def buildPayloadForSubject(text: str , preExistPayload: dict = None, unitTestCreateIndex: int = None):
    retObject = dict()
    retObject["jsonObject"] = {}
    retObject["thinkTime"] = -1

    """
    Process: VUSUnitTestExample1 
    key: 
    task key: 'Unit Test Evaluator'
    task key: 'Unit Test Approver'
    """
    if text.find('Start-VUSUnitTestExample1') != -1:

        print("unitTestCreateIndex", unitTestCreateIndex)

        d = newUTExample1StartData()
        d['name'] = 'John'
        d['counter'] = 1
        retObject["jsonObject"] = {"inputData": d}

    if text.find('Unit Test Evaluator') != -1:

        if preExistPayload != None:
            #print('Unit Test Evaluator')
            #print(json.dumps(preExistPayload, indent=2))

            isReview = preExistPayload["reviewForm"]
            evalForm = preExistPayload["evaluationForm"]
            evalForm["vote"] = 10

            #print(json.dumps(evalForm, indent=2))
            retObject["jsonObject"] = {"evaluationForm": evalForm}

    if text.find('Unit Test Approver') != -1:

        if preExistPayload != None:
            #print('Unit Test Approver')
            #print(json.dumps(preExistPayload, indent=2))

            evalForm = preExistPayload["evaluationForm"]

            #print(json.dumps(evalForm, indent=2))
            retObject["jsonObject"] = {"evaluationForm": evalForm, "reviewForm":False, "promoteRequest":True} 

    return retObject
