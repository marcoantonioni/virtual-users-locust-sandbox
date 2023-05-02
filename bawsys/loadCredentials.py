
import logging,sys,csv,random
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bawSys


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
class CredentialsManager:

    def __init__(self):
        self.userStrategyTwins = False        
        self.user_credentials = []

    def setupCredentials(self, fullPathName, bpmEnvironment : bpmEnv.BpmEnvironment ):
        temp_user_credentials = []        
        
        logging.debug("Loading credentials from: %s", fullPathName)

        self.userStrategy = bpmEnvironment.getValue(bpmEnvironment.keyBAW_USERS_STRATEGY)
        if self.userStrategy != None and self.userStrategy == bpmEnvironment.valBAW_USERS_STRATEGY_TWINS:
            self.userStrategyTwins = True

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
                self.user_credentials.append( temp_user_credentials.pop(idx) )

        logging.debug("Loaded [%d] users, using strategy [%s]", len(self.user_credentials), self.userStrategy)
        

    def getNextUserCredentials(self):
        userCreds = None
        if len(self.user_credentials) > 0:
            userCreds = self.user_credentials.pop()
            if self.userStrategyTwins == True:
                self.user_credentials.insert(0, userCreds)
        else:
            logging.debug("Warning, no more user credential available")
        return userCreds
