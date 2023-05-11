# ==================================
# Python code for JSON schema data model objects
# Application [VirtualUsersSandbox] Acronym [VUS] Snapshot [] Tip [True]
# ==================================

import warlock, json

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

# ----------------------------------
# Class definition for AuthorizationData
# usage samples: youVar = AuthorizationData(), yourVar = AuthorizationData( {...} )
AuthorizationData = warlock.model_factory(jschema_AuthorizationData)


#==========================
# Create Json schema for CCTRData json type
jschema_CCTRData= {
    "name": "CCTRData",
    "properties": {
        "newCounter": {"type": "integer"},
        "requestId": {"type": "string"}},
    "additionalProperties": False
}

# ----------------------------------
# Class definition for CCTRData
# usage samples: youVar = CCTRData(), yourVar = CCTRData( {...} )
CCTRData = warlock.model_factory(jschema_CCTRData)


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

# ----------------------------------
# Class definition for ExampleOfComplexTypesReferences
# usage samples: youVar = ExampleOfComplexTypesReferences(), yourVar = ExampleOfComplexTypesReferences( {...} )
ExampleOfComplexTypesReferences = warlock.model_factory(jschema_ExampleOfComplexTypesReferences)


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

# ----------------------------------
# Class definition for ExampleOfTypes
# usage samples: youVar = ExampleOfTypes(), yourVar = ExampleOfTypes( {...} )
ExampleOfTypes = warlock.model_factory(jschema_ExampleOfTypes)


#==========================
# Create Json schema for UTExample1Data json type
# 'data' of type UTExample1StartData
jschema_UTExample1Data= {
    "name": "UTExample1Data",
    "properties": {
        "data": {"type": "object"},
        "vote": {"type": "integer"}},
    "additionalProperties": False
}

# ----------------------------------
# Class definition for UTExample1Data
# usage samples: youVar = UTExample1Data(), yourVar = UTExample1Data( {...} )
UTExample1Data = warlock.model_factory(jschema_UTExample1Data)


#==========================
# Create Json schema for UTExample1StartData json type
jschema_UTExample1StartData= {
    "name": "UTExample1StartData",
    "properties": {
        "counter": {"type": "integer"},
        "name": {"type": "string"}},
    "additionalProperties": False
}

# ----------------------------------
# Class definition for UTExample1StartData
# usage samples: youVar = UTExample1StartData(), yourVar = UTExample1StartData( {...} )
UTExample1StartData = warlock.model_factory(jschema_UTExample1StartData)


