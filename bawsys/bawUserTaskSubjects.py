"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging, csv, sys, re
import bawsys.bawEnvironment as bpmEnv
import bawsys.bawSystem as bawSys

#--------------------------------------------
def setupTaskSubjects( fullPathNameTaskSubjects ):
    # print("Loading TS from: %s", fullPathNameTaskSubjects)
    
    ts = dict()
    with open(fullPathNameTaskSubjects,'r') as data:
        for item in csv.DictReader(data, skipinitialspace=True, delimiter=','):
            taskSubjectId = bawSys.preparePropertyItem(item, 'TASK_SUBJECTS')
            taskSubjectText = bawSys.preparePropertyItem(item, 'SUBJECT_TEXT')
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
            userId = bawSys.preparePropertyItem(item, 'USER')
            if userId != None and userId != "":
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
                        taskSubjectText = bawSys.preparePropertyItem(item, tsnKey)
                        if taskSubjectText != None:
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
