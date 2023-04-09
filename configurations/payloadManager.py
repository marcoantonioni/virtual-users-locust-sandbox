

def buildPayloadForSubject(taskSubject):

    if taskSubject.find("Compile") != -1:
        return {"inputData": {"requestID": "req1", "counter": 1 ,"authorizedReq": False}}
        pass

    if taskSubject.find("Validate") != -1:
        return {"inputData": {"requestID": "req1", "counter": 2 ,"authorizedReq": True}}
        pass

    return {}
