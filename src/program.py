from comm import PluginCommands, Command
from interface import Interface
from SolverConnection.solver import Solver
from typing import Callable

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
            PluginCommands.HELP: self.help}
        
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
        op : str = self.connection.command("calc_results")
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
        self.interface.output("Closing connection to solver...")
        self.connection.exit()
        self.interface.output("Done!")

        