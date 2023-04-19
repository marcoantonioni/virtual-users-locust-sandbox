#=============================
# import section, add what you need
#=============================
import random

#=============================
# the funcion 'buildPayloadForSubject' must be present in any payload manager
# it must return a dict() object with keys
# jsonObject = your payload in json format
# thinkTime = your particular think thime for the subject in input; if the returned value is -1 the global think thime will be used
#=============================

def buildPayloadForSubject(text):
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
        retObject["jsonObject"] = {'inputData': {'requestId': 'req'+str(rndVal), 'counter': rndVal}}

    if text.find('Compile Data [CCTR]') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'reqCompiled', 'counter': rndVal}}

    if text.find('Validate Data [CCTR]') != -1:
        rndVal : int = random.randint(50, 150) + 1
        retObject["jsonObject"] =  {'inputData': {'requestId': 'reqValidated', 'counter': rndVal}}
        retObject["thinkTime"] = random.randint(0, 5)

    """
    Process: VUSClaimCompleteAuthorize
    key: [CCA]
    task key: 'Compile Request [CCA]'
    task key: 'Authorize Request [CCA]'
    """
    if text.find('Start-VUSClaimCompleteAuthorize') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'req'+str(rndVal), 'counter': rndVal}}

    if text.find('Compile Data [CCA]') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestId': 'reqCompiled', 'counter': rndVal}}

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
        retObject["jsonObject"] =  {'inputData': {'requestId': 'reqValidated', 'counter': rndVal},
                                    'authorizationData': {'authorized': authorize, 'comments': '', 'review': review}}

        retObject["thinkTime"] = random.randint(0, 5)

    return retObject
