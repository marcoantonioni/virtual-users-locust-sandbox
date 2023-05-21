"""
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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

import logging
__log = False

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

    UT_SCENARIO_1 : int = 0
    UT_SCENARIO_2 : int = 1
    UT_SCENARIO_3 : int = 2

    #-------------------------------------------------
    if text.find('Start-VUSUnitTestExample1') != -1:

        if __log:
            logging.info("unitTestCreateIndex [%d]", unitTestCreateIndex)

        d = newUTExample1StartData()

        # Scenarios, with up to 3 instances
        if unitTestCreateIndex == UT_SCENARIO_1:
            d['name'] = 'John'
            d['counter'] = UT_SCENARIO_1

        elif unitTestCreateIndex == UT_SCENARIO_2:
            d['name'] = 'Mary'
            d['counter'] = UT_SCENARIO_2

        elif unitTestCreateIndex == UT_SCENARIO_3:
            d['name'] = 'Hugo'
            d['counter'] = UT_SCENARIO_3
        else:
            raise Exception("Scenario error")

        retObject["jsonObject"] = {"inputData": d}

    #-------------------------------------------------
    if text.find('Unit Test Evaluator') != -1:

        if preExistPayload != None:
            if __log:
                logging.info("Unit Test Evaluator, input payload %s", json.dumps(preExistPayload, indent=2))

            isReview = preExistPayload["reviewForm"]
            evalForm = preExistPayload["evaluationForm"]
            data = evalForm["data"]

            rndVote: int = 0
            # Scenarios
            if data["counter"] == UT_SCENARIO_1:            
                if isReview:
                    # assertion expects: Promoted with vote 6
                    rndVote = 6
                else:
                    rndVote = random.randint(0, 10)

            if data["counter"] == UT_SCENARIO_2:            
                if isReview:
                    raise Exception("Scenario error, cannot be less tahn 6")
                else:
                    rndVote = random.randint(6, 10)

            if data["counter"] == UT_SCENARIO_3:            
                if isReview:
                    # assertion expects: Not promoted with vote less than 6
                    rndVote = random.randint(0, 5)
                else:
                    rndVote = random.randint(0, 3)
            
            evalForm["vote"] = rndVote

            retObject["jsonObject"] = {"evaluationForm": evalForm}

            if __log:
                logging.info("Unit Test Evaluator, output payload %s", json.dumps(retObject, indent=2))

        else:
            raise Exception("Scenario error")

    #-------------------------------------------------
    if text.find('Unit Test Approver') != -1:

        if preExistPayload != None:
            if __log:
                logging.info("Unit Test Approver, input payload %s", json.dumps(preExistPayload, indent=2))

            evalForm = preExistPayload["evaluationForm"]

            mustReview: bool = False
            promoteStudent: bool = False
            if preExistPayload["reviewForm"] == False:
                if evalForm["vote"] < 6:
                    mustReview = True
                else:
                    promoteStudent = True
            else:
                if evalForm["vote"] >= 6:
                    promoteStudent = True

            retObject["jsonObject"] = {"evaluationForm": evalForm, "reviewForm":mustReview, "promoteRequest":promoteStudent} 

            if __log:
                logging.info("Unit Test Approver, output payload %s", json.dumps(retObject, indent=2))

        else:
            raise Exception("Scenario error")

    return retObject
