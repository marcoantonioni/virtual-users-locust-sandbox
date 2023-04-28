import bawsys.commandLineManager as clpm
import bawsys.exposedProcessManager as bpmExpProcs
from bawsys import loadEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
import requests, json, sys, logging, csv
from base64 import b64encode
from bawsys import bawUtils as bawUtils 

class GroupsTeamsManager:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        self.appAcronym = None
        self.appName = None
        self.appSnapName = None 
        self.appSnapTip = None
        self.useTip = False

        self.loggedIn = False
        self.authorizationBearerToken : str = None
        self.cookieTraditional = None
        self.bpmEnvironment = bpmEnvironment
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        self.listOfGroups = []
        self.dictOfGroups = {}
        self.filteredListOfGroupsInfo = []
        
        self.listOfTeams = []
        self.dictOfTeams = {}

        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(bpmEnvironment)
        if runningTraditional == True:
            self.cookieTraditional = bawSys._loginTraditional(self.bpmEnvironment, userName, userPassword)
            if self.cookieTraditional != None:
                self.loggedIn = True
        else:
            self.authorizationBearerToken = bawSys._loginZen(self.bpmEnvironment, userName, userPassword)
            if self.authorizationBearerToken != None:
                self.loggedIn = True

        if self.loggedIn == True:
            if runningTraditional == False:
                self._headers['Authorization'] = 'Bearer '+self.authorizationBearerToken
            else:
                self._headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

    #============================================================
    # Teams
    #============================================================
    def _readGroupsArchive(self, fullPathName):
        # legge file e crea oggetto lista gruppi
        with open(fullPathName,'r') as data:
            for item in csv.DictReader(data):
                groupName = item['GROUP'].strip()
                userName = item['USER'].strip()

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

                # crea oggetto Gruppo e associa utenze
                try:
                    bpmGrpInfo : bawSys.BpmGroupInfo = self.dictOfGroups[groupName]
                    group = bawSys.BpmGroupOperate(groupName, usersList)
                    self.listOfGroups.append(group)
                    if bpmGrpInfo.operateGroup == None:
                        bpmGrpInfo.operateGroup = group
                    else:
                        if bpmGrpInfo.operateGroup.members != None:
                            bpmGrpInfo.operateGroup.members = bpmGrpInfo.operateGroup.members + group.members
                    self.filteredListOfGroupsInfo.append(bpmGrpInfo)
                except:
                    logging.error("_readGroupsArchive error, group '%s' not present on server", groupName)
                    return False
        return True
    
    def _queryGroupList(self):
        ok = False
        # legge lista gruppi da server
        hostUrl : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)

        self.appAcronym : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
        self.appName : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_NAME)
        self.appSnapName : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
        self.appSnapTip : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP)
        self.useTip = False
        if self.appSnapTip.lower() == "true":
            self.useTip = True
        if self.appSnapName == None or self.appSnapName == "":
            self.useTip = True

        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        urlGroups = hostUrl+uriBaseRest+"/groups?includeDeleted=false&parts=all"
        response = requests.get(url=urlGroups, headers=self._headers, verify=False)
        if response.status_code == 200:
            data = response.json()["data"]
            groups = data["groups"]
            #print(json.dumps(groups, indent=2))
            for g in groups:
                grpInfo : bawSys.BpmGroupInfo = bawSys.BpmGroupInfo(g)
                self.dictOfGroups[grpInfo.groupName] = grpInfo

                # print(grpInfo.groupName)
            ok = True
        else:
            logging.error("_queryGroupList error, status code: %d, message: %s", response.status_code, response.text)

        return ok

    def _operateGroups(self, mode : str):
        hostUrl : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST)
        baseUri = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER)
        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/rest/bpm/wle/v1"

        # itera su lista gruppi filtrata e aggiunge/rimuove elenco utenze
        grpInfo : bawSys.BpmGroupInfo = None
        for grpInfo in self.filteredListOfGroupsInfo:
            action = "addMember"
            if mode.lower() == "remove":
                action = "removeMember"
            grpName = grpInfo.groupName
            opGrp : bawSys.BpmGroupOperate = grpInfo.operateGroup
            if opGrp.members != None:
                print("Updating group", grpName)
                for user in opGrp.members:
                    urlGroup = hostUrl+uriBaseRest+"/group/"+grpName+"?action="+action+"&user="+user+"&parts=none"
                    response = requests.put(url=urlGroup, headers=self._headers, verify=False)
                    if response.status_code >= 300:
                        logging.error("_operateGroups error, status code: %d, message: %s", response.status_code, response.text)
                        sys.exit()
        return True
    
    def manageGroups(self, fullPathName: str, mode: str):
        if self._queryGroupList() == True:
            if self._readGroupsArchive(fullPathName) == True:            
                if self._operateGroups(mode) == True:
                    print("Completed groups operations")
                    return True
        return False

    #============================================================
    # Teams
    #============================================================
    def manageTeams(self, fullPathName: str, mode: str):
        if self._queryTeamList() == True:
            if self._readTeamsArchive(fullPathName) == True:            
                if self._operateTeams(mode) == True:
                    print("Completed teams operations")
                    return True
        return False

def manageGroupsTeams(argv):

    ok = False
    if argv != None:
        bpmEnvironment : bpmEnv.BpmEnvironment = bpmEnv.BpmEnvironment()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "e:o:g:t:", ["environment=", "operation=", "groups=", "teams="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathBawEnv = cmdLineMgr.getParam("e", "environment")
            _operation = cmdLineMgr.getParam("o", "operation")
            _fullPathGroupFile = cmdLineMgr.getParam("g", "groups")
            _fullPathTeamsFile = cmdLineMgr.getParam("t", "teams")
            
            bpmEnvironment.loadEnvironment(_fullPathBawEnv)
            bpmEnvironment.dumpValues()

            gtMgr = GroupsTeamsManager(bpmEnvironment)
            if gtMgr.loggedIn == True:
                if _operation != None:
                    if _fullPathGroupFile != None:
                        print("Working on groups...")
                        gtMgr.manageGroups(_fullPathGroupFile, _operation)
                    if _fullPathTeamsFile != None:
                        print("Working on Teams...")
                        gtMgr.manageTeams(_fullPathTeamsFile, _operation)

    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")


def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    manageGroupsTeams(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
