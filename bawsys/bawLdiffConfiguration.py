"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import logging
from jproperties import Properties

class LdifConfiguration:
    configFullPathName : str = None
    configValues : Properties = None

    keyLDIF_DOMAIN_NAME : str = "LDIF_DOMAIN_NAME"
    keyLDIF_DOMAIN_NAME_SUFFIX : str = "LDIF_DOMAIN_NAME_SUFFIX"

    keyLDIF_USER_PREFIX : str = "LDIF_USER_PREFIX"
    keyLDIF_USER_PASSWORD : str = "LDIF_USER_PASSWORD"
    keyLDIF_USERS_TOTAL : str = "LDIF_USERS_TOTAL"

    keyLDIF_GROUP_ALL_USER_PREFIX: str = "LDIF_GROUP_ALL_USER_PREFIX"

    # No spaces in group name, userOffset and totNextUsers are integers
    # userOffset: first user at offset (from 0 to LDIF_LDIF_USERS_TOTAL - 1 from the list of all users 
    # totNextUsers: how match users in the group following the first user at userOffset
    # Line format 
    # [GroupName:userOffset:totNextUsers] | [GroupName:userOffset:totNextUsers]
    keyLDIF_GROUPS : str = "LDIF_GROUPS"

    def loadConfiguration(self, fullPathName):
        self.configFullPathName = fullPathName
        self.configValues = Properties()
        with open(self.configFullPathName, 'rb') as rRrops:
            self.configValues.load(rRrops)

    def getValue(self, key):
        data = None
        cfgVal = self.configValues.get(key)
        if cfgVal != None:
            data = cfgVal.data
        return data

    def dumpValues(self):
        print("*** LDIF CONFIGURATION ***")
        for k in self.configValues.keys():
            cfgVal = self.configValues.get(k)
            if cfgVal != None:
                print(k+"="+cfgVal.data)
        print("***********************")

