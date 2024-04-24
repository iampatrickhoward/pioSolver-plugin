from __future__ import annotations
from enum import Enum
from inputs import Input, FileInput, FolderOf, WeightsFile, BoardFile, Extension, InputType

import unittest

#
class Command:
    def __init__(self, name: str, args: list[Input], helptext: str):
        # name of command
        self.name = name
        # arguments needed
        self.args = args
        self.helptext = helptext
        
    def __str__(self):
        return self.name


class PluginCommands(Enum):
    RUN = Command("run", 
                  [FileInput(Extension.cfr, "Pick a .cfr file to run")],
                  "")
    
    NODELOCK = Command("nodelock",
                       [FolderOf(Extension.cfr, "Pick a folder of .cfr files"),
                        WeightsFile ("Pick a weights file"),
                        BoardFile ("Pick a file with the nodeID and board texture for each .cfr file")],
                       "Allows you to nodelock a folder of files at once.")
                            
    SETTINGS = Command("change accuracy", [Input(InputType.number, "Enter new accuracy as percent of pot")],
                       "Allows you to change accuracy of solver (default is .01)")
    
    END = Command("end", [], "")
    HELP = Command("help", [], "")



#-----------------------------------------------TESTS----------------------------------------------


class Tests(unittest.TestCase):
    def testCommandMap(self):      
        c = Command ("run", {FileInput (Extension.cfr, "Pick a .cfr file to run")})
        self.assertEqual(c.__str__(), "run") 

if __name__ == '__main__': 
    unittest.main() 