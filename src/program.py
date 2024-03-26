from comm import PluginCommands, Command
from interface import Interface, TextInterface
from SolverConnection.solver import Solver
from typing import Callable
import unittest
from global_var import solverPath


class Program:
    
    def __init__(self, connection : Solver, interface : Interface):
        self.connection = connection
        self.interface = interface
        #maintain a mapping of the commands to the functions that run them
        self.commandDispatcher : dict[Command, Callable[[list[str]], None]] = { 
            PluginCommands.RUN: self.run,
            PluginCommands.CHECKFILE: self.checkfile,
            PluginCommands.NODELOCK: self.nodelock,
            PluginCommands.COMPARE: self.compare, 
            PluginCommands.END: self.end,
            PluginCommands.HELP: self.help,
            PluginCommands.DESCRIBE: self.describe_tree}
        
    def start(self) -> None :
        self.takeInput()    
        
        
    def runCommand(self, command : Command, args : list[str]) -> None:
       self.commandDispatcher[command](args)
    
    def takeInput(self):
        inputtedCommand = self.interface.getCommand()
        inputtedArgs = self.interface.getCommandArgs(inputtedCommand.value)
        self.runCommand(inputtedCommand, inputtedArgs)
        if (inputtedCommand != PluginCommands.END):
            self.takeInput()
        
    def run(self, args : list[str]):
        self.connection.command("load_tree \"" + args[0] + "\"")
        self.connection.command("load_all_nodes \"" + args[0] + "\"")
        op = self.connection.command("go")
        self.interface.output("Solver finished")
        
    def describe_tree (self, args : list[str]):
        op = self.connection.command("show_tree_info \"" + args[0] + "\"")
        self.interface.output(op)

    def checkfile (self, arg : list[str]):
        self.interface.output("Checking params file")
        
    def nodelock(self, args : list[str]):
        self.interface.output("nodelocking")

    def compare(self, args : list[str]):
        self.interface.output("comparhing two .cfr files")
    
    def help(self, args : list[str]):
        # we have to explicitly close the solver process
        self.interface.displayOptions()
        
    def end(self, args : list[str]):
        # we have to explicitely close the solver process
        self.connection.exit()
        self.interface.output("Closing connection to solver...done!")

    

class Tests(unittest.TestCase):
    
    def testCommandDispatcher(self):
        p = Program(Solver(solverPath), TextInterface())
        self.assertTrue(callable(p.commandDispatcher[PluginCommands.RUN]))

if __name__ == '__main__': 
    unittest.main() 