"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import bawsys.bawCommandLineManager as clpm
import bawsys.bawExposedProcessManager as bpmExpProcs
from bawsys import bawEnvironment as bpmEnv
from bawsys import bawSystem as bawSys
import requests, json, sys, logging, csv
from json import JSONDecodeError
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
        self.csrfToken = None
        self.bpmEnvironment = bpmEnvironment
        self._headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        self.listOfGroups = []
        self.dictOfGroups = {}
        self.filteredListOfGroupsInfo = []
        
        self.listOfTeams = []
        self.dictOfTeams = {}
        self.filteredListOfTeamInfo = []

        userName = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_NAME)
        userPassword = bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_POWER_USER_PASSWORD)
        runningTraditional = bawSys._isBawTraditional(bpmEnvironment)
        if runningTraditional == True:
            self.cookieTraditional = bawSys._loginTraditional(self.bpmEnvironment, userName, userPassword)
            if self.cookieTraditional != None:
                self.loggedIn = True
        else:
            baseHost : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
            self.csrfToken = bawSys._csrfToken(bpmEnvironment, baseHost, userName, userPassword)
            self.authorizationBearerToken = bawSys._loginZen(self.bpmEnvironment, userName, userPassword)
            if self.authorizationBearerToken != None and self.csrfToken != None:
                self.loggedIn = True

        if self.loggedIn == True:
            if runningTraditional == False:
                self._headers['Authorization'] = 'Bearer '+self.authorizationBearerToken
            else:
                self._headers['Authorization'] = bawUtils._basicAuthHeader(userName, userPassword)

    def _dumpError(self, context, response):
        bpmErrorMessage = ''
        try:
            try:
                jsObj = response.json()
                data = jsObj["Data"]
                bpmErrorMessage = data["errorMessage"]
            except KeyError:
                pass

            logging.error("%s Error, status %d, message %s", context, response.status_code, bpmErrorMessage)

        except JSONDecodeError:
            logging.error("%s Error, response could not be decoded as JSON, status %d", context, response.status_code)
        except KeyError:
            logging.error("%s Error, response did not contain expected key 'Data', 'errorMessage', status %d", context, response.status_code)

    #============================================================
    # Groups
    #============================================================
    def _readGroupsArchive(self, fullPathName : str):
        # legge file e crea oggetto lista gruppi
        with open(fullPathName,'r') as data:
            for item in csv.DictReader(data, skipinitialspace=True):
                groupName = bawSys.preparePropertyItem(item, 'GROUP')
                userName = bawSys.preparePropertyItem(item, 'USER')

                # trim, if teamName empty or start with # then skip line
                if groupName != "":
                    groupName = groupName.strip()
                if groupName.startswith("#") == False:

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
                            else:
                                bpmGrpInfo.operateGroup.members = [] + group.members
                                
                        self.filteredListOfGroupsInfo.append(bpmGrpInfo)
                    except:
                        logging.warning("_readGroupsArchive error, group '%s' not present on server, skipped", groupName)

        return True
    
    def _queryGroupList(self):
        ok = False
        # legge lista gruppi da server
        hostUrl : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
        baseUri : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)

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
            self._dumpError("_queryGroupList", response)

        return ok

    def _operateGroups(self, mode : str):
        hostUrl : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
        baseUri : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)
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
                        self._dumpError("_operateGroups", response)
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

    def _readTeamsArchive(self, fullPathName : str):
        # legge file e crea oggetto lista gruppi
        with open(fullPathName,'r') as data:
            for item in csv.DictReader(data, skipinitialspace=True):
                teamName = bawSys.preparePropertyItem(item, 'TEAM')
                groupName = bawSys.preparePropertyItem(item, 'GROUP')
                userName = bawSys.preparePropertyItem(item, 'USER')
                managerGroup = bawSys.preparePropertyItem(item, 'MANAGER')

                # trim, if teamName empty or start with # then skip line
                if teamName != "":
                    teamName = teamName.strip()
                if teamName.startswith("#") == False:
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

                    # crea oggetto Team e associa utenze
                    try:
                        bpmTeamInfo : bawSys.TeamBindingInfo = self.dictOfTeams[teamName]
                        team = bawSys.TeamBindingOperate(teamName, groupName, usersList, managerGroup)
                        self.listOfTeams.append(team)
                        if bpmTeamInfo.operateTeam == None:
                            bpmTeamInfo.operateTeam = team
                        else:
                            bpmTeamInfo.operateTeam.managerGroup = managerGroup
                            if bpmTeamInfo.operateTeam.groups != None:
                                bpmTeamInfo.operateTeam.groups = bpmTeamInfo.operateTeam.groups + [groupName]
                            else:
                                bpmTeamInfo.operateTeam.groups = [groupName]

                            if bpmTeamInfo.operateTeam.members != None:
                                bpmTeamInfo.operateTeam.members = bpmTeamInfo.operateTeam.members + usersList
                            else:
                                bpmTeamInfo.operateTeam.members = [] + usersList
                        
                        self.filteredListOfTeamInfo.append(bpmTeamInfo)
                    except:
                        logging.warning("_readTeamsArchive error, Team '%s' not present on server, skipped", teamName)

        return True
    
    def _queryTeamList(self):
        ok = False
        # legge lista gruppi da server
        hostUrl : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
        baseUri : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)

        self.appAcronym : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
        self.appSnapName : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
        self.appSnapTip : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_USE_TIP)
        self.useTip = False
        if self.appSnapTip.lower() == "true":
            self.useTip = True
        if self.appSnapName == None or self.appSnapName == "":
            self.useTip = True
        if self.useTip == True:
            logging.error("Cannot operate on team bindings with Tip configuration, change the configuration to point to a NON tip snapshot")
            return False

        if baseUri == None:
            baseUri = ""

        uriBaseRest = baseUri+"/ops/std/bpm/containers"

        self._headers['BPMCSRFToken'] = self.csrfToken

        urlTeamBindings = hostUrl+uriBaseRest+"/"+self.appAcronym+"/versions/"+self.appSnapName+"/team_bindings"
        response = requests.get(url=urlTeamBindings, headers=self._headers, verify=False)
        if response.status_code == 200:
            team_bindings = response.json()["team_bindings"]
            for t in team_bindings:
                teamInfo : bawSys.TeamBindingInfo = bawSys.TeamBindingInfo(t)
                self.dictOfTeams[teamInfo.name] = teamInfo
            ok = True
        else:
            self._dumpError("_queryTeamList", response)

        return ok

    def _operateTeams(self, mode : str):
        ok = False
        # legge lista gruppi da server
        hostUrl : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_HOST), False)
        baseUri : str = bawUtils.removeSlash(self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_BASE_URI_SERVER), False)
        self.appAcronym : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_ACRONYM)
        self.appSnapName : str = self.bpmEnvironment.getValue(bpmEnv.BpmEnvironment.keyBAW_PROCESS_APPLICATION_SNAPSHOT_NAME)
        if baseUri == None:
            baseUri = ""
        uriBaseRest = baseUri+"/ops/std/bpm/containers"
        self._headers['BPMCSRFToken'] = self.csrfToken
        urlTeamBindingsBase = hostUrl+uriBaseRest+"/"+self.appAcronym+"/versions/"+self.appSnapName+"/team_bindings/"

        teamInfo : bawSys.TeamBindingInfo = None 
        for teamInfo in self.filteredListOfTeamInfo:
            urlUpdate = urlTeamBindingsBase + teamInfo.name            
            print("Updating team", teamInfo.name)
            response = None
            data = {}
            if mode.lower() == 'add':
                data["set_auto_refresh_enabled"] = True
                if teamInfo.operateTeam.members != None:
                    data["add_users"] = teamInfo.operateTeam.members
                if teamInfo.operateTeam.groups != None:
                    data["add_groups"] = teamInfo.operateTeam.groups
                if teamInfo.operateTeam.managerGroup != None:
                    data["add_manager"] = teamInfo.operateTeam.managerGroup

                # print(json.dumps(data, indent = 2))

                response = requests.post(url=urlUpdate, headers=self._headers, json=data, verify=False)
            else:
                if teamInfo.operateTeam.members != None:
                    data["remove_users"] = teamInfo.operateTeam.members
                if teamInfo.operateTeam.groups != None:
                    data["remove_groups"] = teamInfo.operateTeam.groups
                if teamInfo.operateTeam.managerGroup != None:
                    data["remove_manager"] = teamInfo.operateTeam.managerGroup

                # print(json.dumps(data, indent = 2))

                response = requests.delete(url=urlUpdate, headers=self._headers, json=data, verify=False)
            
            if response.status_code >= 300:
                self._dumpError("_operateTeams", response)
                ok = False
                break

        return ok
    
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
            else:
                print("Not logged in")
    if ok == False:
        print("Wrong arguments, use -e param to specify environment file")


def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    manageGroupsTeams(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
