import random

def buildPayloadForSubject(text):

    if text.find('Start-ClaimCompileAndValidate') != -1:
        rndVal : int = random.randint(0, 100) + 1
        return {'inputData': {'requestID': 'req'+str(rndVal), 'counter': rndVal ,'authorizedReq': False}}
        pass

    if text.find('Compile') != -1:
        rndVal : int = random.randint(0, 100) + 1
        return {'inputData': {'requestID': 'reqCompiled', 'counter': rndVal ,'authorizedReq': False}}
        pass

    if text.find('Validate') != -1:
        rndVal : int = random.randint(0, 100) + 1
        return {'inputData': {'requestID': 'reqValidated', 'counter': rndVal ,'authorizedReq': True}}
        pass

    return {}
