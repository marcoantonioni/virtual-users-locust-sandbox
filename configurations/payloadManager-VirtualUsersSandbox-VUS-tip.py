# ==================================
# Python code for data model objects
# Application [VirtualUsersSandbox] Acronym [VUS] Snapshot [] Tip [tip]
# ==================================

#==========================
# Create AuthorizationData json object
def newAuthorizationData():
    return {"authorized": False, "comments": "", "review": False}


#==========================
# Create CCTRData json object
def newCCTRData():
    return {"newCounter": 0, "requestId": ""}


#==========================
# Create ExampleOfComplexTypesReferences json object
# 'authorizationData' of type AuthorizationData
# 'cctrData' of type CCTRData
def newExampleOfComplexTypesReferences():
    return {"authorizationData": {}, "cctrData": {}}


#==========================
# Create ExampleOfTypes json object
def newExampleOfTypes():
    return {"attrBool": False, "attrDate": None, "attrDecimal": 0.0, "attrInt": 0, "attrListBool": [], "attrListDate": [], "attrListDecimal": [], "attrListInt": [], "attrListText": [], "attrListTime": [], "attrText": "", "attrTime": None}


# ==================================
# Python code for JSON schema data model objects
# Application [VirtualUsersSandbox] Acronym [VUS] Snapshot [] Tip [tip]
# ==================================

#==========================
# Create Json schema for AuthorizationData json type
jschema_AuthorizationData= {
    "name": "AuthorizationData",
    "properties": {
        "authorized": {"type": "boolean"},
        "comments": {"type": "string"},
        "review": {"type": "boolean"}},
    "additionalProperties": False
}


#==========================
# Create Json schema for CCTRData json type
jschema_CCTRData= {
    "name": "CCTRData",
    "properties": {
        "newCounter": {"type": "integer"},
        "requestId": {"type": "string"}},
    "additionalProperties": False
}


#==========================
# Create Json schema for ExampleOfComplexTypesReferences json type
# 'authorizationData' of type AuthorizationData
# 'cctrData' of type CCTRData
jschema_ExampleOfComplexTypesReferences= {
    "name": "ExampleOfComplexTypesReferences",
    "properties": {
        "authorizationData": {"type": "object"},
        "cctrData": {"type": "object"}},
    "additionalProperties": False
}


#==========================
# Create Json schema for ExampleOfTypes json type
jschema_ExampleOfTypes= {
    "name": "ExampleOfTypes",
    "properties": {
        "attrBool": {"type": "boolean"},
        "attrDate": {"type": "string"},
        "attrDecimal": {"type": "number"},
        "attrInt": {"type": "integer"},
        "attrListBool": {"type": "array", "items": { "type": "boolean" }},
        "attrListDate": {"type": "array", "items": { "type": "string" }},
        "attrListDecimal": {"type": "array", "items": { "type": "number" }},
        "attrListInt": {"type": "array", "items": { "type": "integer" }},
        "attrListText": {"type": "array", "items": { "type": "string" }},
        "attrListTime": {"type": "array", "items": { "type": "string" }},
        "attrText": {"type": "string"},
        "attrTime": {"type": "string"}},
    "additionalProperties": False
}


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

    # !!! The following code is an example, remove it if not needed

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
