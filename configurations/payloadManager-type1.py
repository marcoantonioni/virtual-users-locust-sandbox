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

    if text.find('Start-VUSClaimCompleteTwoRoles') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestID': 'req'+str(rndVal), 'counter': rndVal ,'authorizedReq': False}}

    if text.find('Compile') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestID': 'reqCompiled', 'counter': rndVal ,'authorizedReq': False}}

    if text.find('Validate') != -1:
        rndVal : int = random.randint(50, 150) + 1
        retObject["jsonObject"] =  {'inputData': {'requestID': 'reqValidated', 'counter': rndVal ,'authorizedReq': True}}
        retObject["thinkTime"] = random.randint(0, 5)

    if text.find('Start-VUSClaimCompleteAuthorize') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestID': 'req'+str(rndVal), 'counter': rndVal ,'authorizedReq': False}}

    return retObject
