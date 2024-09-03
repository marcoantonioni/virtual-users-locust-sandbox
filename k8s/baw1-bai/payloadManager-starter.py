"""
https://opensource.org/license/mit/
MIT License

Copyright 2023 Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

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
    idx = taskSubjectText.find(subjectFromUserDictionary)
    # print("=====> isMatchingTaskSubject: ", taskSubjectText, subjectFromUserDictionary, idx)
    return idx != -1

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

    # print("//// buildPayloadForSubject=", text)

    """
    Process: VUSLoanRequest
    key: 
    task key: 'Evaluate Loan Request Data'
    task key: 'Validate Loan Request Data'
    """
    if text.find('Start-VUSLoanRequest') != -1:
        rndVal : int = random.randint(0, 100) + 1        
        retObject["jsonObject"] = {
            'loanRequest': {
                'userName': 'customer'+str(rndVal), 
                'amountRequested': random.randint(10000, 100000), 
                'loanDurationMonths': random.randint(12, 120), 
                'requestorAnnualNetIncome': random.randint(200000, 500000),
                'activeLoans': random.randint(0, 2),
                'badPayer': False,
                'challengeYourLuck': False
            }
        }
        # print(json.dumps(retObject["jsonObject"], indent=2))
        
        ttMin = 1
        ttMax = 2
        retObject["thinkTime"] = random.randrange(ttMin, ttMax, 1)

    if text.find('Evaluate Loan Request Data') != -1:
        if preExistPayload != None:
            loanRequest = preExistPayload["loanRequest"]
            installmentAmount = preExistPayload["installmentAmount"]
            requestorMonthlyNetIncome = preExistPayload["requestorMonthlyNetIncome"]
            riskLevel = preExistPayload["riskLevel"]

            # print(json.dumps(loanRequest, indent=2))
            # print("installmentAmount", installmentAmount)
            # print("requestorMonthlyNetIncome", requestorMonthlyNetIncome)
            # print("riskLevel", riskLevel)
        rejected = False
        rndVal : int = random.randrange(0, 10, 1)
        if rndVal == 0:
            rejected = True
        retObject["jsonObject"] = {'rejected': rejected} 

        ttMin = 10
        ttMax = 20
        retObject["thinkTime"] = random.randrange(ttMin, ttMax, 1)

    if text.find('Validate Loan Request Data') != -1:
        if preExistPayload != None:
            loanRequest = preExistPayload["loanRequest"]
            installmentAmount = preExistPayload["installmentAmount"]
            requestorMonthlyNetIncome = preExistPayload["requestorMonthlyNetIncome"]
            riskLevel = preExistPayload["riskLevel"]
            
            # print(json.dumps(loanRequest, indent=2))
            # print("installmentAmount", installmentAmount)
            # print("requestorMonthlyNetIncome", requestorMonthlyNetIncome)
            # print("riskLevel", riskLevel)
        loanAccepted = False
        rndVal : int = random.randrange(0, 5, 1)
        if rndVal > 0:
            loanAccepted = True
        retObject["jsonObject"] =  {'loanAccepted': loanAccepted}

        ttMin = 5
        ttMax = 10
        retObject["thinkTime"] = random.randrange(ttMin, ttMax, 1)

    """
    Process: VUSClaimCompleteTwoRoles 
    key: [CCTR]
    task key: 'Compile Request [CCTR]'
    task key: 'Authorize Request [CCTR]'
    """
    if text.find('Start-VUSClaimCompleteTwoRoles') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'req'+str(rndVal), 'newCounter': rndVal}}

    if text.find('Compile Data [CCTR]') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'reqCompiled', 'newCounter': rndVal}}

    if text.find('Validate Data [CCTR]') != -1:
        rndVal : int = random.randint(50, 150) + 1

        if preExistPayload != None:
            # update prev values
            inputData = preExistPayload["inputData"]
            inputData["newCounter"] = rndVal
            retObject["jsonObject"] = {'inputData': inputData} 
        else:
            # new values
            retObject["jsonObject"] =  {'inputData': {'requestId': 'reqValidated', 'newCounter': rndVal}}

        retObject["thinkTime"] = random.randint(0, 5)

    """
    Process: VUSClaimCompleteAuthorize
    key: [CCA]
    task key: 'Compile Request [CCA]'
    task key: 'Authorize Request [CCA]'
    """
    if text.find('Start-VUSClaimCompleteAuthorize') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'req'+str(rndVal), 'newCounter': rndVal}}

    if text.find('Compile Data [CCA]') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'reqCompiled', 'newCounter': rndVal}}

    if text.find('Validate Data [CCA]') != -1:
        authorize = False
        review = False

        rndReview : int = random.randint(0, 1) + 1
        if rndReview != 0:
            review = True
        if review == False:
            rndAuth : int = random.randint(0, 1) + 1
            if rndAuth != 0:
                authorize = True

        rndVal : int = random.randint(50, 150) + 1

        if preExistPayload != None:
            # update prev values
            inputData = preExistPayload["inputData"]
            inputData["newCounter"] = rndVal
            authorizationData = preExistPayload["authorizationData"]
            authorizationData["authorized"] = authorize
            authorizationData["review"] = review
            retObject["jsonObject"] =  {'inputData': inputData, 'authorizationData': authorizationData}
        else:
            retObject["jsonObject"] =  {'inputData': {'requestId': 'reqValidated', 'newCounter': rndVal},
                                        'authorizationData': {'authorized': authorize, 'comments': '', 'review': review}}

        retObject["thinkTime"] = random.randint(0, 5)

    return retObject
