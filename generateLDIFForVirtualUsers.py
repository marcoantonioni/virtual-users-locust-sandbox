"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys, logging
import bawsys.bawCommandLineManager as clpm
from bawsys import bawLdiffConfiguration as bawLdif

class LdifUser:
    """
    A class to represent an LDIF user record.

    Attributes:
        userName (str): The username and Surname of the user.
        password (str): The password for the user.
        domainName (str): The domain name of the user.
        domainNameSuffix (str): The domain name suffix of the user.
        uidNumber (int): The user ID number of the user.
        gidNumber (int): The group ID number of the user.

    Methods:
        getUserName(): Returns the username of the user.
        formatLdifRecord(): Returns the LDIF record for the user.
    """    
    def __init__(self, userName: str, password: str, domainName: str, domainNameSuffix: str, uidNumber: int, gidNumber: int):
        self.userName: str = userName
        self.password: str = password
        self.domainName = domainName
        self.domainNameSuffix = domainNameSuffix
        self.uidNumber = uidNumber
        self.gidNumber = gidNumber
        pass

    def getUserName(self):
        return self.userName
    
    def formatLdifRecord(self):
        record = "dn: uid="+self.userName+",dc="+self.domainName+",dc="+self.domainNameSuffix+"\n"
        record += "uid: "+self.userName+"\n"
        record += "cn: "+self.userName+"\n"
        record += "sn: "+self.userName+"\n"
        record += "userpassword: "+self.password+"\n"
        record += "objectClass: top\n"
        record += "objectClass: posixAccount\n"
        record += "objectClass: organizationalPerson\n"
        record += "objectClass: inetOrgPerson\n"
        record += "objectClass: person\n"
        record += "uidNumber: "+str(self.uidNumber)+"\n"
        record += "gidNumber: "+str(self.gidNumber)+"\n"
        record += "homeDirectory: /home/"+self.userName+"/\n"
        record += "mail: "+self.userName+"@"+self.domainName+"."+self.domainNameSuffix+"\n"
        # record += "\n"
        return record
    
class LdifGroup:
    """
    LdifGroup class to represent a group in an LDAP directory.

    Attributes:
        groupName (str): The name of the group.
        domainName (str): The name of the domain.
        domainNameSuffix (str): The suffix of the domain.
        users (LdifUser): The users belonging to the group.

    Methods:
        getGroupName(): Returns the name of the group.
        formatLdifRecord(): Returns a formatted LDIF record for the group.
    """    
    def __init__(self, groupName: str, domainName: str, domainNameSuffix: str, users: LdifUser):
        self.groupName: str = groupName
        self.domainName = domainName
        self.domainNameSuffix = domainNameSuffix
        self.users: LdifUser = users
        pass

    def getGroupName(self):
        return self.groupName

    def formatLdifRecord(self):
        baseDomain = "dc="+self.domainName+",dc="+self.domainNameSuffix
        record = "dn: cn="+self.groupName+","+baseDomain+"\n"
        record += "objectClass: groupOfNames\n"
        record += "objectClass: top\n"
        record += "cn: "+self.groupName+"\n"
        for user in self.users:
            record += "member: uid="+user.getUserName()+","+baseDomain+"\n"

        return record

class UserRangeForGroup:
    """
    A class to represent a user range for a specific group.

    Attributes:
        groupName (str): The name of the group.
        lowRange (int): The lower range of the user.
        highRange (int): The higher range of the user.

    Methods:
        __init__(groupName: str, lowRange: int, highRange: int): Initializes the UserRangeForGroup object with the given parameters.
    """    
    def __init__(self, groupName: str, lowRange: int, highRange: int):
        self.groupName = groupName
        self.lowRange = lowRange
        self.highRange = highRange

class LdifGenerator:
    """
    LdifGenerator is a class for generating LDIF records for users and groups.

    Attributes:
        domainName (str): The domain name.
        domainNameSuffix (str): The domain name suffix.
        userPrefix (str): The user prefix.
        userPassword (str): The user password.
        allUsers (LdifUser): A list of LdifUser objects.
        allGroups (LdifGroup): A list of LdifGroup objects.
        allGroupsByName (dict): A dictionary of LdifGroup objects by name.
        listOfUserRangesForGroups (UserRangeForGroup): A list of user ranges for groups.
        gidNumber (int): The group ID number.
        uidNumber (int): The user ID number.

    Methods:
        createUsers(totUsers: int) -> None: Creates users based on the total number of users.
        rangeOfUsers(offset: int, totUsers: int) -> LdifUser: Returns a range of users based on the offset and total number of users.
        createGroup(groupName: str, offset: int, totUsers: int) -> None: Creates a group with the specified name, offset, and total number of users.
        buildGroupInfo(ldifDomain: str, ldifGroupsInfo: str, ldifAllUsersGroupPrefix: str) -> None: Builds group information based on the LDIF domain, groups info, and all users group prefix.
        generateLdif(_fullOutputPath: str) -> None: Generates LDIF records and writes them to a file or prints them to the console.
        generateUserCredentials(_fullOutputPath: str) -> None: Generates user credentials and writes them to a file or prints them to the console.
    """    
    def __init__(self, domainName: str, domainNameSuffix: str, userPrefix: str, userPassword: str):
        self.domainName: str  = domainName
        self.domainNameSuffix = domainNameSuffix
        self.allUsers: LdifUser = []
        self.allGroups: LdifGroup = []
        self.allGroupsByName: dict = dict()
        self.listOfUserRangesForGroups: UserRangeForGroup = []
        self.userPrefix = userPrefix
        self.userPassword = userPassword
        self.gidNumber = 5555
        self.uidNumber = 12340000

    def createUsers(self, totUsers: int):
        userIdx = 1
        while userIdx <= totUsers:
            user = LdifUser(self.userPrefix+str(userIdx), self.userPassword, self.domainName, self.domainNameSuffix, self.uidNumber+userIdx, self.gidNumber)
            self.allUsers.append(user)
            userIdx += 1

    def rangeOfUsers(self, offset: int, totUsers: int):
        users: LdifUser = []
        maxLen = len(self.allUsers)
        if offset < 0:
            offset = 0
        if (offset+totUsers) > maxLen:
            totUsers = maxLen - offset
        maxIdx = offset + totUsers
        while offset < maxIdx:
            users.append(self.allUsers[offset])
            offset += 1
        return users

    def createGroup(self, groupName: str, offset: int, totUsers: int):
        users = self.rangeOfUsers(offset, totUsers)
        group: LdifGroup = LdifGroup(groupName, self.domainName, self.domainNameSuffix, users)
        self.allGroups.append(group)
        self.allGroupsByName[groupName] = group

    def buildGroupInfo(self, ldifDomain: str, ldifGroupsInfo : str, ldifAllUsersGroupPrefix: str):
        self.createGroup(ldifAllUsersGroupPrefix+"-"+ldifDomain, 0, len(self.allUsers))

        ldifGroupsInfo = ldifGroupsInfo.strip()
        ldifGroupsInfo = ldifGroupsInfo.replace(" ", "")
        segments = ldifGroupsInfo.split("|")
        for segment in segments:
            if segment.count("[") > 1 or segment.count("]") > 1:
                print("ERROR: missing separator for: "+segment)
            
            segment = segment.removeprefix("[")
            segment = segment.removesuffix("]")
            groupData = segment.split(":")
            groupName = groupData[0]
            try:
                self.allGroupsByName[groupName]
                print("ERROR: duplicate group name: "+groupName)
                sys.exit()
            except KeyError:
                groupUserOffset = 0
                groupUserTot = 0
                items = len(groupData)
                if (items > 1):
                    try:
                        groupUserOffset = int(groupData[1])
                        if (items > 2):
                            groupUserTot = int(groupData[2])
                    except ValueError:
                        groupUserOffset = 0
                        groupUserTot = 0
                    
                self.createGroup(groupName, groupUserOffset, groupUserTot)

    def generateLdif(self, _fullOutputPath):
        if _fullOutputPath != None:
            f = open(_fullOutputPath, "a")
            f.truncate(0)

            f.writelines("version: 1")
            f.writelines("\r\n\r\n")
            for user in self.allUsers:            
                f.writelines(user.formatLdifRecord())
                f.writelines("\r\n")
            for group in self.allGroups:            
                f.writelines(group.formatLdifRecord())
                f.writelines("\r\n")
            f.close()
        else:
            print("\n\n===== LDIF RECORDS =====\n\n")
            for user in self.allUsers:            
                print(user.formatLdifRecord())
            for group in self.allGroups:            
                print(group.formatLdifRecord())
        print("\n\nGenerated "+str(len(self.allUsers))+" users and "+str(len(self.allGroups))+" groups")

    def generateUserCredentials(self, _fullOutputPath):
        if _fullOutputPath != None:
            f = open(_fullOutputPath, "a")
            f.truncate(0)
            f.writelines("NAME,PASSWORD,EMAIL")
            f.writelines("\r\n")
            for user in self.allUsers:            
                f.writelines(user.userName+","+user.password+",none@nowhere.net")
                f.writelines("\r\n")
            f.close()
        else:
            print("\n\n===== USER CREDENTIALS =====\n\n")
            print("NAME,PASSWORD,EMAIL")
            for user in self.allUsers:            
                print(user.userName+","+user.password+",none@nowhere.net"+"\n")
        print("\n\nGenerated "+str(len(self.allUsers))+" set of credentials")

def createLdif(argv):
    """
    Creates LDIF file with users and groups.

    Parameters:
    argv (list): List of command line arguments.

    Returns:
    None
    """    
    if argv != None:
        ok = False
        ldifCfg : bawLdif.LdifConfiguration = bawLdif.LdifConfiguration()
        cmdLineMgr = clpm.CommandLineParamsManager()
        cmdLineMgr.builDictionary(argv, "c:l:u:", ["config=", "ldif=", "users="])
        if cmdLineMgr.isExit() == False:
            ok = True
            _fullPathLdifCfg = cmdLineMgr.getParam("c", "config")
            _fullOutputPathLdif = cmdLineMgr.getParam("l", "ldif")
            _fullOutputPathUsersCredentials = cmdLineMgr.getParam("u", "users")
            ldifCfg.loadConfiguration(_fullPathLdifCfg)
            ldifCfg.dumpValues()

            ldifDomain = ldifCfg.getValue(ldifCfg.keyLDIF_DOMAIN_NAME)
            ldifDomainSuffix = ldifCfg.getValue(ldifCfg.keyLDIF_DOMAIN_NAME_SUFFIX)
            ldifUserPrefix = ldifCfg.getValue(ldifCfg.keyLDIF_USER_PREFIX)
            ldifUserPassword = ldifCfg.getValue(ldifCfg.keyLDIF_USER_PASSWORD)
            ldifUserTotal = int(ldifCfg.getValue(ldifCfg.keyLDIF_USERS_TOTAL).strip())
            ldifGroupsInfo = ldifCfg.getValue(ldifCfg.keyLDIF_GROUPS)
            ldifAllUsersGroupPrefix = ldifCfg.getValue(ldifCfg.keyLDIF_GROUP_ALL_USER_PREFIX)

            ldifGenerator: LdifGenerator = LdifGenerator(ldifDomain, ldifDomainSuffix, ldifUserPrefix, ldifUserPassword)
            ldifGenerator.createUsers(ldifUserTotal)
            ldifGenerator.buildGroupInfo(ldifDomain, ldifGroupsInfo, ldifAllUsersGroupPrefix)

            ldifGenerator.generateLdif(_fullOutputPathLdif)
            ldifGenerator.generateUserCredentials(_fullOutputPathUsersCredentials)

    if ok == False:
        print("Wrong arguments, use -l 'filename' param to specify ldif configuration file")

def main(argv):
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)    
    createLdif(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
