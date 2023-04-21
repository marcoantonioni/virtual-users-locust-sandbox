from bawsys import loadEnvironment as bpmEnv
import bawsys.commandLineManager as clpm
import bawsys.loadCredentials as creds
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
        logging.error("_accessToken error, status code: %d, messge: %s", response.status_code, response.text)
    return access_token

# CP4BA address (cpd-cp4ba)
def _cp4baToken(baseHost, userName, iamToken):
    cp4ba_token : str = None
    my_headers = {'username': userName, 'iam-token': iamToken }    
    response = requests.get(url=baseHost+"/v1/preauth/validateAuth", headers=my_headers, verify=False)
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
        logging.error("_cp4baToken error, status code: %d, messge: %s", response.status_code, response.text)
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
        logging.error("_csrfToken error, status code: %d, messge: %s", response.status_code, response.text)
    return access_token

"""


# IAM address (cp-console)
def _userOnboard(bpmEnvironment : bpmEnv.BpmEnvironment, users, domainName):
        access_token : str = None
        hostUrl : str = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        iamUrl = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_HOST)
        powerUser = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_USER_NAME)
        powerUserPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_IAM_USER_PASSWORD)
        access_token : str = _accessToken(iamUrl, powerUser, powerUserPassword)
        if access_token != None:
            zenToken = _cp4baToken(hostUrl, powerUser, access_token)
            if zenToken != None:
                params = []
                user: creds.UserCredentials = None 
                for user in users:
                    userName = user.getName()
                    userMail = user.getEmail()
                    if userName != None and userMail != None and domainName != None and userName != "" and userMail != "" and domainName != "":
                        jsonUserInfo = { 
                                        'username':userName, 'displayName':userName, 'email':userMail,
                                        'authenticator':'external', 'user_roles':['zen_user_role'],
                                        'misc':{ 'realm_name':domainName, 'extAttributes':{} }
                                        }
                        params.append( jsonUserInfo )
                    else:
                        logging.error("_userOnboard error, wrong parameter values userName[%s], userMail[%s] domainName[%s]", userName, userMail, domainName)

                my_headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Bearer '+zenToken}
                response = requests.post(url=hostUrl+"/usermgmt/v1/user/bulk", headers=my_headers, json=params, verify=False)
                if logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug("_onboardUser status code: %s", response.status_code)
                if response.status_code == 200:
                    try:
                        respJson = response.json()
                        print(respJson)
                        respResult = respJson["result"]
                        respMsgCode: str = respJson["_messageCode_"]
                        respMessage = respJson["message"]
                        for rr in respResult:
                            resultUserUid = rr["uid"]
                            resultUserName = rr["username"]
                            resultUserSuccess = rr["success"]
                            resultUserMessage = rr["message"]
                            if respMsgCode.lower() == "success":
                                logging.info("User [%s] onboarded in domain [%s], message[%s], new user id[%s]", resultUserName, domainName, resultUserMessage, resultUserUid )
                            else:
                                logging.error("ERROR _onboardUser, username[%s], message code[%s] message[%s] %s", resultUserName, respMsgCode, respMessage, resultUserMessage)
                    except JSONDecodeError:
                        logging.error("_onboardUser error, response could not be decoded as JSON")
                        response.failure("Response could not be decoded as JSON")
                    except KeyError:
                        logging.error("_onboardUser error, did not contain expected key 'access_token'")
                        response.failure("Response did not contain expected key 'access_token'")
                else:
                    logging.error("_userOnboard error, status code: %d, messge: %s", response.status_code, response.text)


def testUserOnboard(bpmEnvironment : bpmEnv.BpmEnvironment, userName, userMail, domainName):
    #user: creds.UserCredentials = creds.UserCredentials(userName, None, userMail)
    #users = [user] 

    creds.setupCredentials("./configurations/creds10.csv", bpmEnvironment)
    
    _userOnboard(bpmEnvironment, creds.user_credentials, domainName)

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    

    bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
    cmdLineMgr = clpm.CommandLineParamsManager()
    cmdLineMgr.builDictionary(argv, "e:u:m:d:", ["environment=","user=","mail=","domain="])
    if cmdLineMgr.isExit() == False:
        ok = True
        _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
        userName = cmdLineMgr.getParam("u", "user")
        userMail = cmdLineMgr.getParam("m", "mail")
        domainName = cmdLineMgr.getParam("d", "domain")
        bpmEnvironment.loadEnvironment(_fullPathBawEnv)
        bpmEnvironment.dumpValues()
        testUserOnboard(bpmEnvironment, userName, userMail, domainName)

if __name__ == "__main__":
    main(sys.argv[1:])
