from enum import Enum

class OutputTypes:
    
    def outputEV(self, ev):
        print("EV: \t" & ev)
    
    def outputActionFrequencies(self, frequ):
        print("to be determined")


class InputTypes (Enum):
    CFR = ".cfr"
    CSV = ".csv"
    
class Commands(Enum):
    RUN = "run"
    CHECKFILE = "checkfile"
    NODELOCK = "nodelock"
    COMPARE = "compare"
    END = "end"
    HELP = "help"
    
class CommandDetails:
    argMap = {Commands.RUN: {InputTypes.CFR},
              Commands.CHECKFILE: {InputTypes.CSV},
              Commands.NODELOCK: {InputTypes.CFR, InputTypes.CSV},
              Commands.COMPARE: {InputTypes.CFR, InputTypes.CFR}}
    
    