
import logging,sys,csv,random
import bawsys.loadEnvironment as bpmEnv

#--------------------------------------------
# global vars
temp_user_credentials = []
user_credentials = []

#--------------------------------------------
class UserCredentials:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def getName(self):
        return self.name

    def getPassword(self):
        return self.password
    
    pass

#--------------------------------------------
userStrategyTwins = False

def setupCredentials( fullPathName, bpmEnvironment : bpmEnv.BpmEnvironment  ):
    global userStrategyTwins

    logging.debug("Loading credentials from: %s", fullPathName)

    userStrategy = bpmEnvironment.getValue(bpmEnvironment.keyBAW_USERS_STRATEGY)
    if userStrategy != None and userStrategy == bpmEnvironment.valBAW_USERS_STRATEGY_TWINS:
        userStrategyTwins = True

    with open(fullPathName,'r') as data:
        for item in csv.DictReader(data):
            userName = item['NAME'].strip()
            userPassword = item['PASSWORD'].strip()
            temp_user_credentials.append(UserCredentials(userName, userPassword))
            logging.debug('User %s, password %s', userName, userPassword)
    
    hasItems = True
    while hasItems:
        numUsers = len(temp_user_credentials)
        idx = 0
        if numUsers > 1:
            idx = random.randint(0, numUsers - 1)
        else:
            hasItems = False
        user_credentials.append( temp_user_credentials.pop(idx) )

    logging.debug("Loaded [%d] users, using strategy [%s]", len(user_credentials), userStrategy)
    
    pass        

def getNextUserCredentials():
    if len(user_credentials) > 0:
        user = user_credentials.pop()
        if userStrategyTwins == True:
            user_credentials.insert(0, user)
        return user
    else:
        logging.error("********************************")
        logging.error("!!! Error no more users")
        logging.error("********************************")
        return None

    pass
