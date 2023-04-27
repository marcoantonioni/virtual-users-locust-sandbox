# ==================================
# Python code for data model objects
# Application [VirtualUsersSandbox] Acronym [VUS] Snapshot [0.3.2] Tip [true]
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


import json
def main():
    print(json.dumps(newAuthorizationData(),indent=4))
    print(json.dumps(newCCTRData(),indent=4))
    cctr = newExampleOfComplexTypesReferences()
    cctr["cctrData"] = newCCTRData()
    cctr["authorizationData"] = newAuthorizationData()
    print(json.dumps(cctr,indent=4))
    print(json.dumps(newExampleOfTypes(),indent=4))

if __name__ == "__main__":
    main()
