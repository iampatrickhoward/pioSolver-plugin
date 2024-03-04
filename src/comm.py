from enum import Enum
from inputs import *

#
class Command ():
    def __init__(self, name : str, args : list[Input]):
        #name of command
        self.name = name
        #arguments needed
        self.args = args
        
    def runCommand(self, program, args):
        program.commandDispatcher[self](args)


class CommandList(Enum):
    RUN = Command ("run", {FileInput (Extension.cfr, "Pick a .cfr file to run")})
    
    CHECKFILE = Command ("checkfile", {ParamsFileInput ("Enter a params file to check")})
    
    NODELOCK = Command ("nodelock", {FileInput (Extension.cfr, "Pick a .cfr file to nodelock"), 
                                     ParamsFileInput ("Pick a file with nodelocking parameters")})
    
    COMPARE = Command ("compare", {FileInput (Extension.cfr, "Pick the first .cfr file"),
                                   FileInput (Extension.cfr, "Pick the second .cfr file")})
    END = Command ("end", {})
    HELP = ("help",{})
    

def getCommandNames() -> list[str]:
    names = {}
    for c in CommandList:
        names.append(c.value.name)
    return names
    