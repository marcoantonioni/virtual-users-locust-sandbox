from bawsys import loadEnvironment as bpmEnv
import bawsys.commandLineManager as clpm
from bawsys import bawSystem as bawSys
import sys, logging, json
from json import JSONDecodeError
import requests

import http
requests.packages.urllib3.disable_warnings() 

import urllib3


# !!!!!! /BAS

# IAM address (cp-console)
def _accessToken(baseHost, userName, userPassword):
    access_token : str = None
    params : str = "grant_type=password&username="+userName+"&password="+userPassword+"&scope=openid"
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}
    response = requests.post(url=baseHost+"/idprovider/v1/auth/identitytoken", data=params, headers=my_headers, verify=False)
                                           
    #print("",userName,userPassword)
    #print("_accessToken")
    #print(json.dumps(response.json(), indent = 2 ))

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("_accessToken status code: %s", response.status_code)
    if response.status_code == 200:
        try:
            access_token = response.json()["access_token"]                
        except JSONDecodeError:
            logging.error("_accessToken error, user %s, response could not be decoded as JSON", userName)
            response.failure("Response could not be decoded as JSON")
        except KeyError:
            logging.error("_accessToken error, user %s, did not contain expected key 'access_token'", userName)
            response.failure("Response did not contain expected key 'access_token'")
    else:
        print(json.dumps(response.json(), indent = 2 ))
    return access_token

# CP4BA address (cpd-cp4ba)
def _cp4baToken(baseHost, userName, iamToken):
    cp4ba_token : str = None
    my_headers = {'username': userName, 'iam-token': iamToken }
    
    response = requests.get(url=baseHost+"/v1/preauth/validateAuth", headers=my_headers, verify=False)
    
    #print("_cp4baToken")
    #print(json.dumps(response.json(), indent = 2 ))
    
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("_cp4baToken status code: %s", response.status_code)
    if response.status_code == 200:
        try:
            cp4ba_token = response.json()["accessToken"]                
        except JSONDecodeError:
            logging.error("_cp4baToken error, user %s, response could not be decoded as JSON", userName)
            response.failure("Response could not be decoded as JSON")
        except KeyError:
            logging.error("_cp4baToken error, user %s, did not contain expected key 'accessToken'", userName)
            response.failure("Response did not contain expected key 'accessToken'")
    else:
        print(json.dumps(response.json(), indent = 2 ))
    return cp4ba_token

"""
# !!!! /BAS
def _csrfToken(baseHost, userName, userPassword):
    access_token : str = None
    my_headers = {'Content-Type': 'application/json'}
    basic = HTTPBasicAuth(userName, userPassword)
    response = requests.post(url=baseHost+"/bas/bpm/system/login", headers=my_headers, data="{}", verify=False, auth=basic)
    
    print("",userName,userPassword)
    print(baseHost+"/bas/bpm/system/login")
    print("_csrfToken")
    print(json.dumps(response.json(), indent = 2 ))

    if logging.getLogger().isEnabledFor(logging.DEBUG):
        logging.debug("_csrfToken status code: %s", response.status_code)
    if response.status_code < 300:
        try:
            access_token = response.json()["csrf_token"]                
        except JSONDecodeError:
            logging.error("_accessToken error, user %s, response could not be decoded as JSON", userName)
            response.failure("Response could not be decoded as JSON")
        except KeyError:
            logging.error("_accessToken error, user %s, did not contain expected key 'access_token'", userName)
            response.failure("Response did not contain expected key 'access_token'")
    else:
        print(json.dumps(response.json(), indent = 2 ))
    return access_token

"""


# IAM address (cp-console)
def _userOnboard(bpmEnvironment : bpmEnv.BpmEnvironment, userName, domainName):
    access_token : str = None
    hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
    iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)

    powerUser = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_USER_NAME)
    powerUserPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_USER_PASSWORD)
    
    access_token : str = _accessToken(iamUrl, powerUser, powerUserPassword)
    if access_token != None:
        zenToken = _cp4baToken(hostUrl, powerUser, access_token)

        #print("")
        #print("")
        #print("user ", powerUser, powerUserPassword)
        #print("URL per iamtoken: ", iamUrl)
        #print("URL per zentoken: ", hostUrl)
        #print("iamtoken: ",access_token)
        #print("zentoken: ",zenToken)
        #print("")
        #print("")

        if zenToken != None:

            params = [{
                        'username':userName,
                        'displayName':userName,
                        'email':userName+'@vuxdomain.org',
                        'authenticator':'external',
                        'user_roles':['zen_user_role'],
                        'misc':{
                            'realm_name':domainName,                        
                            'extAttributes':{}
                            }
                    }]
                    
            my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+zenToken}

            response = requests.post(url=hostUrl+"/usermgmt/v1/user/bulk", headers=my_headers, json=params, verify=False)

            print(json.dumps(response.json(), indent = 2 ))
            
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug("_onboardUser status code: %s", response.status_code)
            if response.status_code == 200:
                try:
                    """
                    {
                    "result": [
                        {
                        "uid": "1000331033",
                        "username": "vuxuser9",
                        "displayName": "vuxuser9",
                        "success": "true",
                        "message": "User created"
                        }
                    ],
                    "_messageCode_": "Success",
                    "message": "Success"
                    }

                    {
                    "result": [
                        {
                        "uid": "",
                        "username": "vuxuser5",
                        "displayName": "vuxuser5",
                        "success": "false",
                        "message": "username_exist"
                        }
                    ],
                    "_messageCode_": "Success",
                    "message": "Success"
                    }

                    # utente non esistente, dominio valido, lo crea senza controllare esistenza !!!
                    {
                    "result": [
                        {
                        "uid": "1000331034",
                        "username": "anonimo",
                        "displayName": "anonimo",
                        "success": "true",
                        "message": "User created"
                        }
                    ],
                    "_messageCode_": "Success",
                    "message": "Success"
                    }

                    # utente NON esistente e dominio NON valido, lo crea senza controllare esistenza !!!
                    {
                    "result": [
                        {
                        "uid": "1000331035",
                        "username": "anonimobis",
                        "displayName": "anonimobis",
                        "success": "true",
                        "message": "User created"
                        }
                    ],
                    "_messageCode_": "Success",
                    "message": "Success"
                    }

                    """
                    print("OK")              
                except JSONDecodeError:
                    logging.error("_onboardUser error, user %s, response could not be decoded as JSON", userName)
                    response.failure("Response could not be decoded as JSON")
                except KeyError:
                    logging.error("_onboardUser error, user %s, did not contain expected key 'access_token'", userName)
                    response.failure("Response did not contain expected key 'access_token'")
            else:
                print(response.status_code)
                # print(json.dumps(response.json(), indent = 2 ))


def testUserOnboard(bpmEnvironment : bpmEnv.BpmEnvironment, userName, domainName):
    _userOnboard(bpmEnvironment, userName, domainName)

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    

    bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
    cmdLineMgr = clpm.CommandLineParamsManager()
    cmdLineMgr.builDictionary(argv, "e:u:d:", ["environment=","user=","domain="])
    if cmdLineMgr.isExit() == False:
        ok = True
        _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
        userName = cmdLineMgr.getParam("u", "user")
        domainName = cmdLineMgr.getParam("d", "domain")

        bpmEnvironment.loadEnvironment(_fullPathBawEnv)
        bpmEnvironment.dumpValues()
        testUserOnboard(bpmEnvironment, userName, domainName)

if __name__ == "__main__":
    main(sys.argv[1:])
