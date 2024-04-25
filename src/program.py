from __future__ import annotations
from menu import PluginCommands, Command
from interface import Interface, TextInterface, GUInterface
from treeops import TreeOperator
from inputs import WeightsFile, BoardFile
from stringFunc import removeExtension, timestamp
from SolverConnection.solver import Solver
from solverCommands import SolverCommmand
from typing import Callable
from fileIO import CSVio, IO
import unittest
from global_var import solverPath
import asyncio
import win32api


consoleLog = True

class Program:
    
    def __init__(self, connection : Solver, interface : Interface):
        self.connection = connection
        self.command = SolverCommmand(connection)
        self.interface = interface
        #maintain a mapping of the commands to the functions that run them
        self.commandDispatcher : dict[Command, Callable[[list[str]], None]] = { 
            PluginCommands.RUN: self.get_results,
            PluginCommands.NODELOCK: self.nodelock_and_save,
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
    
    def tryFunction(self, func , args : list):
        try:
            #command not meant to have any inputs
            if args is None or len(args) == 0:
                return func()
            #command meant to take a single input
            elif len(args) == 1:
                return func(args[0])
            #command meant to take a list of
            else:
                return func(args)
        except Exception as e:
            self.interface.output(str(e))
            return None
        
    # arg[0] = node
    # returns the action frequencies for the sister and children nodes of the target node
    def getAllFrequencies(self, args: list) :
        nodeID = args[0]
        treeOp = TreeOperator(self.connection, nodeID)
        sisterFrequencies = []
        childFrequencies = []
        for s in treeOp.sisters:
            #sisterFrequencies[s] = self.getActionFrequency(s)
            sisterFrequencies.append(self.getActionFrequency(s))
        for c in childFrequencies:
            #childFrequencies[c] = self.getActionFrequency(c)
            childFrequencies.append(self.getActionFrequency(c))
    
        return [sisterFrequencies, childFrequencies]
        
    

    
    # args[0][0] : the folder path
    # args[0][1] : list of .cfr files
    # args[1] : the name you want for the result file
    # args[2] : either a string with the nodeID or a map with .cfr file names -> file-specific nodeIDs
    def get_results(self, args: list[str]):
        folder, cfrFiles = args[0]
        path = folder + "\\results\\" + args[1] + ".csv"
        nodeBook = args[2]
        pio = SolverCommmand(self.connection)
        
        # arrays that will be written to CSV file
        toCSV = []
        title = ["File", "Node"]
        
        toCSV.append(title)
        needsTitles = True
        
        for cfr in cfrFiles:
            self.tryFunction(pio.load_tree, [folder + "\\" + cfr])
            # The line `nodeID = self.tryFunction(self.get_file_nodeID, [cfr, nodeBook])` is calling
            # the `tryFunction` method with arguments `self.get_file_nodeID` as the function to try
            # and `[cfr, nodeBook]` as the arguments to pass to that function.
            nodeID = self.tryFunction(self.get_file_nodeID, [cfr, nodeBook])
            if nodeID:
                thisLine = [cfr, nodeID]
            
                treeOp = TreeOperator(connection = self.connection, nodeID = nodeID)
            
                #append action frequencies at this node
                if needsTitles is True:
                    title.append("frequencies at node")
                thisLine.append("   ")
                
                for s in treeOp.sisters:
                    if needsTitles is True:
                        title.append(s)
                    thisLine.append(str(pio.getActionFrequency([s])))
                
                #append action frequencies after this node
                if needsTitles is True:
                    title.append("frequencies after node")
                thisLine.append("   ")
                
            
                children = treeOp.getChildIDs(nodeID)
                for c in children:
                    if needsTitles is True:
                        title.append(c)
                    thisLine.append(str(pio.getActionFrequency([c])))
                
                # for whatever reason, if you cannot get the line frequencies after running the solver, 
                if needsTitles is True:
                        title.extend(["", "EV OOP", "EV IP"])
                thisLine.append("   ")
                
                # append EVs to line
                evs = self.tryFunction(pio.getEV, [])
                if evs:
                    thisLine.extend(evs)
                
                toCSV.append(thisLine)
                
            needsTitles = False
            
        CSVio.addRows(path, toCSV)
        
    #args[0] : file Name
    #args[1] : either a string with the nodeID or a map with .cfr file names -> file-specific nodeIDs
    def get_file_nodeID(self, args: list[str]):
        file, nodeBook = args
        match nodeBook:
            # there is only one node
            case str():
                return nodeBook
            # each file has unique node
            case dict():
                # check if file is in nodeBook
                if (file in nodeBook):
                    return nodeBook[file]
                # perhaps the user entered file names sans extension
                elif (removeExtension(file) in nodeBook):
                    return nodeBook[removeExtension(file)]
                else:
                    raise Exception(file + "not specific in board file.")
                    
    # args[0][0] : the folder path
    # args[0][1] : list of .cfr files
    # args[1] : map of category names -> weights
    # args[2] : either a string with the nodeID or a map with .cfr file names -> file-specific nodeIDs
    def nodelock_and_save(self, args : list[str]):
        folder, cfrFiles = args[0]
        categWeights = args[1]
        nodeBook = args[2]
        pio = SolverCommmand(self.connection)
        path = folder + "\\" + "NODELOCK_" + timestamp() + "\\"
    
        
        for cfr in cfrFiles:
            print(pio.load_tree(folder + "\\" + cfr))
            nodeID = self.tryFunction(self.get_file_nodeID, [cfr, nodeBook])
            if nodeID:
                treeOp = TreeOperator(self.connection, nodeID)
                treeOp.set_strategy([categWeights, nodeID].copy())
                self.interface.output("Strategy set for " + cfr)
                pio.saveTree([path + cfr])
                

        
        self.interface.output("Done!")
    
    def help(self, args : list[str]):
        # we have to explicitly close the solver process
        self.interface.displayOptions()
        
    def end(self, args : list[str]):
        # we have to explicitely close the solver process
        self.connection.exit()
        self.interface.output("Closing connection to solver...done!")

    

class Tests(unittest.TestCase):
    def __init__(self, methodName: solverPath = "runTest") -> None:
        super().__init__(methodName)
        self.oneFile = ["KdTc9h_small.cfr"]
        self.allFiles = ["KdTc9h_small.cfr", "Qh6c5s_small.cfr", "As5h3s_small.cfr"]
        self.sampleFolder = r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample"
        self.p = Program(Solver(solverPath), GUInterface())
        self.simple_weights = WeightsFile("test").parseInput(self.sampleFolder + r"\simple_weights.json")
        self.exception_weights = WeightsFile("test").parseInput(self.sampleFolder + r"\exception_weights.json")
        self.all_weights = WeightsFile("test").parseInput(self.sampleFolder + r"\all_to_hundred.json")
        self.b = BoardFile("test").parseInput(self.sampleFolder + r"\board_simple.json")
        
    def testCommandDispatcher(self):
        self.assertTrue(callable(self.p.commandDispatcher[PluginCommands.RUN]))
        
    def testSolve(self):
        self.p.get_results([[self.sampleFolder + "\\cfr", self.oneFile],"testResults" + timestamp(),self.b])
        self.p.end([])
    
    def testNordelock(self):
        self.p.nodelock_and_save([[self.sampleFolder + "\\cfr", self.oneFile], self.all_weights, self.b])
        self.p.end([])
        
if __name__ == '__main__': 
    unittest.main() 

