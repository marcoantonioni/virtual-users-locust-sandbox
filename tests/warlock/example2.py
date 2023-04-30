
import warlock
import json

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

#---------------------------------------------
AuthorizationData = warlock.model_factory(jschema_AuthorizationData)
CCTRData = warlock.model_factory(jschema_CCTRData)
ExampleOfComplexTypesReferences = warlock.model_factory(jschema_ExampleOfComplexTypesReferences)
ExampleOfTypes = warlock.model_factory(jschema_ExampleOfTypes)

#---------------------------------------------
authData = AuthorizationData()
authData.authorized = True
authData.review = True
authData.comments = "this is a comment"

print(json.dumps(authData, indent=2))

#---------------------------------------------
cctrData = CCTRData()
cctrData.newCounter = 234
cctrData.requestId = "id23"

print(json.dumps(cctrData, indent=2))

#---------------------------------------------
cTypesRef = ExampleOfComplexTypesReferences()
cTypesRef.authorizationData = authData
cTypesRef.cctrData = cctrData

print(json.dumps(cTypesRef, indent=2))

#---------------------------------------------
types = ExampleOfTypes()
types.attrBool = False
types.attrDate = "20230430T00:10:00Z"
types.attrDecimal = 12.34
types.attrInt = 543
types.attrListBool = [True, False]
types.attrListDate = ["20230430T00:20:00Z", "20230430T00:21:00Z", "20230430T00:22:00Z"]
types.attrListDecimal = [ 0.1, 0.2, 0.3]
types.attrListInt = [ 2, 4, 6 ]
types.attrListText = ["text1", "text2"]
types.attrListTime = ["20230430T00:10:00Z", "20230430T00:11:00Z", "20230430T00:12:00Z"]
types.attrText = "this is a text"
types.attrTime = "20230430T00:10:00Z"

print(json.dumps(types, indent=2))
