from enum import Enum
from inputs import Input, InputType, FileInput, Extension, ParamsFileInput

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

    CHECKFILE = Command("checkfile",
                        [ParamsFileInput("Enter a params file to check")],
                       "")

    NODELOCK = Command(
        "nodelock",
        [
            FileInput(Extension.cfr, "Pick a .cfr file to nodelock"),
            ParamsFileInput("Pick a file with nodelocking parameters"),
        ], ""
    )

    COMPARE = Command(
        "compare",
        [
            FileInput(Extension.cfr, "Pick the first .cfr file"),
            FileInput(Extension.cfr, "Pick the second .cfr file"),
        ],
        "")
    
    END = Command("end", [], "")
    HELP = Command("help", [], "")
    DESCRIBE = Command("describe", [FileInput(Extension.cfr, "Pick a .cfr file")], "")



#-----------------------------------------------TESTS----------------------------------------------


class Tests(unittest.TestCase):
    def testCommandMap(self):      
        c = Command ("run", {FileInput (Extension.cfr, "Pick a .cfr file to run")})
        self.assertEqual(c.__str__(), "run") 

if __name__ == '__main__': 
    unittest.main() 