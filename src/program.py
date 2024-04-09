from comm import PluginCommands, Command
from interface import Interface, TextInterface
from nodelock import NodeLocker
from logging_tools import parseResults, getDirectoryofFile
from SolverConnection.solver import Solver
from typing import Callable
from fileIO import fileWriter
import unittest
from global_var import solverPath


class Program:
    
    def __init__(self, connection : Solver, interface : Interface):
        self.connection = connection
        self.interface = interface
        #maintain a mapping of the commands to the functions that run them
        self.commandDispatcher : dict[Command, Callable[[list[str]], None]] = { 
            PluginCommands.RUN: self.run,
            PluginCommands.NODELOCK: self.nodelock,
            PluginCommands.END: self.end,
            PluginCommands.HELP: self.help}
         
    def start(self) -> None :
        self.commandRun()    
        
    
    def commandRun(self):
        inputtedCommand = self.interface.getCommand()
        inputtedArgs = self.interface.getCommandArgs(inputtedCommand.value)
        if inputtedArgs is None:
            return self.commandDispatcher[PluginCommands.END]([])
        # runs the function in the program class associated with that command
        self.commandDispatcher[inputtedCommand](inputtedArgs)
        if (inputtedCommand != PluginCommands.END):
            self.commandRun()
    
    
    def load_tree(self, cfrFilePath) :
        self.connection.command("load_tree \"" + cfrFilePath + "\"")
        self.connection.command("load_all_nodes")
        self.interface.output(cfrFilePath + " loaded.")
    
    def solve_and_publish(self, results_file_path) :
        self.connection.command("go")
        self.connection.command("wait_for_solver")
        op = self.connection.command("calc_results") 
        values = parseResults(op)
        fileWriter.mapToCSV(results_file_path, values)    
        self.interface.output("Done! results written to " + results_file_path)
        
    # args[0] .cfr file
    # args[1] name of results file
    # EV OOP and EV IP and ignore the other values
    def run(self, args : list[str]):
        self.load_tree(args[0])
        # publish results to csv file w similar name (remove.cfr) in same folder
        self.solve_and_publish(args[0][:-4] + "_results.csv")

    
    # args[0] : list of .cfr files
    # args[1] : map of category names -> weights
    # args[2] : either a string with the nodeID or a map with .cfr file names -> file-specific nodeIDs
    def nodelock(self, args : list[str]):
        folder = args[0][0]
        files = args[0][1]
        categWeights = args[1]
        nodeID = args[2]
        
        nodelocker = NodeLocker(self.connection)
        for fName in files:
            self.load_tree(folder + fName)
            match nodeID:
                case str():
                    nodelocker.set_strategy(categWeights, nodeID)
                    self.output("Strategy set for " + fName)
                    self.solve_and_publish(folder + fName + nodeID)
                case dict():
                    fileSpecificNodeID = nodeID[fName]
                    if fileSpecificNodeID is not None:
                        nodelocker.set_strategy(categWeights, fileSpecificNodeID)
                        self.output("Strategy set for " + fName)
                        self.solve_and_publish(folder + fName + "_" + + categWeights + "_" + fileSpecificNodeID + "_results.csv")
            
        self.interface.output("Done!")
    
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