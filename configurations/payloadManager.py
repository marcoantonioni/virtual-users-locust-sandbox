

def buildPayloadForSubject(text):

    if text.find("Compile") != -1:
        return {"inputData": {"requestID": "req1", "counter": 1 ,"authorizedReq": False}}
        pass

    if text.find("Validate") != -1:
        return {"inputData": {"requestID": "req1", "counter": 2 ,"authorizedReq": True}}
        pass

    return {}
