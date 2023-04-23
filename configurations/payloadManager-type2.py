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

    if text.find('Start-ClaimCompileAndValidate') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestID': 'NOTIMPreq'+str(rndVal), 'counter': rndVal ,'authorizedReq': False}}

    if text.find('Compile') != -1:
        rndVal : int = random.randint(0, 100) + 1
        retObject["jsonObject"] = {'inputData': {'requestID': 'NOTIMPreqCompiled', 'counter': rndVal ,'authorizedReq': False}}

    if text.find('Validate') != -1:
        rndVal : int = random.randint(50, 150) + 1
        retObject["jsonObject"] =  {'inputData': {'requestID': 'NOTIMPreqValidated', 'counter': rndVal ,'authorizedReq': True}}
        retObject["thinkTime"] = random.randint(0, 5)

    return retObject
