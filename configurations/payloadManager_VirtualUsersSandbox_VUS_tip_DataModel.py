# ==================================
# Python code for data model objects
# Application [VirtualUsersSandbox] Acronym [VUS] Snapshot [] Tip [True]
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


#==========================
# Create UTExample1Data json object
# 'data' of type UTExample1StartData
def newUTExample1Data():
    return {"data": {}, "vote": 0}


#==========================
# Create UTExample1StartData json object
def newUTExample1StartData():
    return {"counter": 0, "name": ""}


