#=============================
# import section, add what you need
#=============================
import random

#=============================
# the funcion 'buildPayloadForSubject' must be present in any payload manager
# it must return a Boolean, True when taskSubjectText match the subjext in a dictionary
# the default logic is: search as substring
# reimplement it as from your needs
#=============================

def isMatchingTaskSubject(taskSubjectText, subjectFromUserDictionary):
    return taskSubjectText.find(subjectFromUserDictionary) != -1

#=============================
# the funcion 'buildPayloadForSubject' must be present in any payload manager
# it must return a dict() object with keys
# jsonObject = your payload in json format
# thinkTime = your particular think thime for the subject in input; if the returned value is -1 the global think thime will be used
# reimplement it as from your needs
#=============================

def buildPayloadForSubject(text, preExistPayload = None):
    retObject = dict()
    retObject["jsonObject"] = {}
    retObject["thinkTime"] = -1

    """
    Process: VUSClaimCompleteTwoRoles 
    key: [CCTR]
    task key: 'Compile Request [CCTR]'
    task key: 'Authorize Request [CCTR]'
    """
    if text.find('Start-VUSClaimCompleteTwoRoles') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'req'+str(rndVal), 'counterX': rndVal}}

    if text.find('Compile Data [CCTR]') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'reqCompiled', 'counterX': rndVal}}

    if text.find('Validate Data [CCTR]') != -1:
        rndVal : int = random.randint(50, 150) + 1

        if preExistPayload != None:
            # update prev values
            inputData = preExistPayload["inputData"]
            inputData["counterX"] = rndVal
            retObject["jsonObject"] = {'inputData': inputData} 
        else:
            # new values
            retObject["jsonObject"] =  {'inputData': {'requestId': 'reqValidated', 'counterX': rndVal}}

        retObject["thinkTime"] = random.randint(0, 5)

    """
    Process: VUSClaimCompleteAuthorize
    key: [CCA]
    task key: 'Compile Request [CCA]'
    task key: 'Authorize Request [CCA]'
    """
    if text.find('Start-VUSClaimCompleteAuthorize') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'req'+str(rndVal), 'counterX': rndVal}}

    if text.find('Compile Data [CCA]') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'reqCompiled', 'counterX': rndVal}}

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
            inputData["counterX"] = rndVal
            authorizationData = preExistPayload["authorizationData"]
            authorizationData["authorized"] = authorize
            authorizationData["review"] = review
            retObject["jsonObject"] =  {'inputData': inputData, 'authorizationData': authorizationData}
        else:
            retObject["jsonObject"] =  {'inputData': {'requestId': 'reqValidated', 'counterX': rndVal},
                                        'authorizationData': {'authorized': authorize, 'comments': '', 'review': review}}

        retObject["thinkTime"] = random.randint(0, 5)

    return retObject
