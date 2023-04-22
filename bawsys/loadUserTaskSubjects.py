
# test: python ./mytasks/loadUserTaskSubjects.py  | sed "s/'/\"/g" | jq .

import logging, csv, sys, re
import bawsys.loadEnvironment as bpmEnv
import bawsys.bawSystem as bawSys

#--------------------------------------------
def setupTaskSubjects( fullPathNameTaskSubjects ):
    # print("Loading TS from: %s", fullPathNameTaskSubjects)
    
    ts = dict()
    with open(fullPathNameTaskSubjects,'r') as data:
        for item in csv.DictReader(data, skipinitialspace=True, delimiter=','):
            taskSubjectId = item['TASK_SUBJECTS'].strip()
            taskSubjectText = item['SUBJECT_TEXT'].strip()
            item = {'taskSubjectId': taskSubjectId, 'taskSubjectText': taskSubjectText}
            ts[taskSubjectId] = item
            # print("taskSubjectId ["+taskSubjectId+"] taskSubjectText ["+taskSubjectText+"]")    
    return ts

def setupUserTaskSubjects( fullPathNameUserTaskSubjects ):
    # print("Loading US-TS from: %s", fullPathNameUserTaskSubjects)
    uts = dict()
    with open(fullPathNameUserTaskSubjects,'r') as data:
        dictReader = csv.DictReader(data, skipinitialspace=True, delimiter=',')
        fieldNamesCount = len(dictReader.fieldnames)
        for item in dictReader:
            userId = item['USER'].strip()
            if userId != "":
                usersList = []
                rangeOfUsers = bawSys.usersRange( userId )
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
                    usersList.append(userId)
                taskSubjects = []
                for idx in range(fieldNamesCount-1):
                    try:
                        tsnKey = "TSN"+str(idx+1)
                        taskSubjectText = item[tsnKey].strip()
                        taskSubjects.append(taskSubjectText)
                    except:
                        pass

                for uid in usersList:
                    uts[uid] = taskSubjects
    return uts

def createUserSubjectsDictionary(userTaskSubjects, taskSubjects):
    usd = dict()
    for userId in userTaskSubjects:
        tsList = userTaskSubjects[userId]
        taskTexts = []
        for idx in range(len(tsList)):
            try:
                k = tsList[idx]
                text = taskSubjects[k]["taskSubjectText"]
                # print("userId ["+userId+"] k["+k+"] text["+text+"]")
                taskTexts.append(text)
            except:
                pass
        usd[userId] = taskTexts
    return usd

class BpmUserSubjects:
    userSubjectsDictionary : dict = None

    def setDictionary(self, dictionary):
        self.userSubjectsDictionary = dictionary

    def getDictionary(self):
        return self.userSubjectsDictionary

#----------------------------------
"""

def main():
    #tasks_subjects = setupTaskSubjects("./configurations/TS-TEST1.csv")
    #user_task_subjects = setupUserTaskSubjects("./configurations/US-TS-TEST1.csv")
    #userSubjectsDictionary = createUserSubjectsDictionary(user_task_subjects, tasks_subjects)
    #print(userSubjectsDictionary)

    print( usersRange( "vuxuser1..vuxuser100" ) )
    print( usersRange( "vuxuser24..vuxuser32" ) )
    print( usersRange( "vuxuser43" ) )
    print( usersRange( "vuxuser10..vuxser3" ) )
    print( usersRange( "vuxuser1..vuuser100" ) )

if __name__ == "__main__":
    main()

"""
