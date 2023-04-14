import sys
import getopt


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
