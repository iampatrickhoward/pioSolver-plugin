import unittest
from interface import Interface, TextInterface, GUInterface
from comm import PluginCommands



class Tests(unittest.TestCase):

    def testInstantiation(self):
        # make sure names of commands are properly populated in map
        i = Interface()
        for c in PluginCommands:
            self.assertIn(c.value.name, i.commandMap)
        #make sure inputGetterMap returns functions
        for n in i.inputGetterMap.values():
            self.assertIs(callable(n), True)
    
    def testGetCommandArgs(self):
        i = TextInterface()
        # make sure names of commands are properly populated in map
        # args = i.getCommandArgs(PluginCommands.RUN.value)
        # print(args)
        
    def testGUI(self): # show an "Open" dialog box and return the path to the selected file
        i = GUInterface()
        print(i.getCommand())
        print(i.getText())
        print(i.getFilePath())
        i.output("testing")


if __name__ == '__main__': 
    unittest.main() 