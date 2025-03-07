"""
https://opensource.org/license/mit/
MIT License

Author: Antonioni Marco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys, getopt


class CommandLineParamsManager:
    
    def __init__(self):
        self.arguments = {}
    

    def builDictionary(self, argv, options, extendedOptions):
        try:
            opts, args = getopt.getopt(argv, options, extendedOptions)
            for opt, arg in opts:
                opt = opt.replace("-", "")
                if opt in options or opt+"=" in extendedOptions:
                    self.arguments[opt] = arg
        except:
            self.arguments["__exit__"] = "true"

    def isExit(self):
        exit = False
        try:
            exit = self.arguments["__exit__"] == "true"
        except:
            pass
        return exit
    
    def getParam(self, opt, extOpt):
        param = None
        try:
            if opt != None:
                param =self.arguments[opt]
            else:
                if extOpt != None:
                    param =self.arguments[extOpt]
        except:
            pass
        return param
    
    def dumpArguments(self):
        print(self.arguments)


#---------------------------------------
def test(argv):
    envFullPath = None

    cmdLineParamsMgr = CommandLineParamsManager()

    cmdLineParamsMgr.builDictionary(argv, "e:", ["environment="])

    cmdLineParamsMgr.dumpArguments()

    if cmdLineParamsMgr.isExit():
        sys.exit()

    envFullPath = cmdLineParamsMgr.getParam("e", None)
    print('Env opt file is ', envFullPath)
    envFullPath = cmdLineParamsMgr.getParam(None, "environment")
    print('Env extOpt file is ', envFullPath)

if __name__ == "__main__":
    test(sys.argv[1:])
