
import logging,sys,csv,random
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bawSys

#--------------------------------------------
# global vars
temp_user_credentials = []
user_credentials = []

#--------------------------------------------
class UserCredentials:
    def __init__(self, name, password, email):
        self.name = name
        self.password = password
        self.email = email

    def getName(self):
        return self.name

    def getPassword(self):
        return self.password
    
    def getEmail(self):
        return self.email
    
    pass

#--------------------------------------------
userStrategyTwins = False

def setupCredentials( fullPathName, bpmEnvironment : bpmEnv.BpmEnvironment ):
    global userStrategyTwins

    logging.debug("Loading credentials from: %s", fullPathName)

    userStrategy = bpmEnvironment.getValue(bpmEnvironment.keyBAW_USERS_STRATEGY)
    if userStrategy != None and userStrategy == bpmEnvironment.valBAW_USERS_STRATEGY_TWINS:
        userStrategyTwins = True

    with open(fullPathName,'r') as data:
        for item in csv.DictReader(data):
            userName = bawSys.preparePropertyItem(item, 'NAME')
            if userName == None or userName.startswith('#'):
                continue

            userPassword = bawSys.preparePropertyItem(item, 'PASSWORD')
            if userPassword == None or userPassword == "":
                logging.error('User %s skipped, has no password.', userName)
                continue

            userEmail = bawSys.preparePropertyItem(item, 'EMAIL')
            if userEmail == None:
                userEmail = ""

            usersList = []
            rangeOfUsers = bawSys.usersRange( userName )
            if rangeOfUsers != None:
                userFrom = rangeOfUsers["infoFrom"]
                userTo = rangeOfUsers["infoTo"]
                idxFrom = userFrom["number"]
                idxTo = userTo["number"]
                namePrefix = userFrom["name"]
                totUsers = (idxTo - idxFrom) + 1
                i = 0
                while idxFrom <= idxTo:
                    usersList.append(namePrefix+str(idxFrom))
                    idxFrom += 1                    
            else:
                usersList.append(userName)

            for usr in usersList:
                temp_user_credentials.append(UserCredentials(usr, userPassword, userEmail))
                logging.debug('User %s, password %s, email %s', usr, userPassword, userEmail)
    
    orderMode = 0
    userOrderMode = bpmEnvironment.getValue(bpmEnvironment.keyBAW_USER_ORDER_MODE)
    if userOrderMode != None:
        if userOrderMode == bpmEnvironment.valBAW_USER_ORDER_MODE_SORTED_FIFO:
            orderMode = 0
        if userOrderMode == bpmEnvironment.valBAW_USER_ORDER_MODE_SORTED_LIFO:
            orderMode = 1
        if userOrderMode == bpmEnvironment.valBAW_USER_ORDER_MODE_SORTED_RANDOM:
            orderMode = 2


    hasItems = True
    while hasItems:
        numUsers = len(temp_user_credentials)
        idx = 0
        if numUsers > 0:
            if orderMode == 0:
                idx = 0
            if orderMode == 1:
                idx = numUsers - 1
            if orderMode == 2:
                idx = random.randint(0, numUsers - 1)
        else:
            hasItems = False
        if hasItems == True:
            user_credentials.append( temp_user_credentials.pop(idx) )

    logging.debug("Loaded [%d] users, using strategy [%s]", len(user_credentials), userStrategy)
    

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
