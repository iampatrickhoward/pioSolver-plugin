
from __future__ import annotations
from stringFunc import parseEV, toFloat, parseTreeInfoToMap, parseSettingsToMap
import unittest
from global_var import solverPath
from SolverConnection.solver import Solver
from treeops import TreeOperator, normalizeWeight, nodeInfo

consoleLog = False

# functions that transmit commands to the solver to get correct output
class SolverCommmand():
    def __init__(self, connection) -> None:
        self.connection = connection
    
    

    def tryPio(self, func, args : list): 
        if consoleLog:
            for a in args:
                print("---- " + a)
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
            self.connection.exit()
            raise e
        
    
    def run_until(self, command, confirmation):
        self.tryPio(self.connection.write_line, [command])
        self.tryPio(self.connection.wait_line, [confirmation])
        self.tryPio(self.connection.read_until_end, [])
        
    def load_tree(self, cfrFilePath) :
        self.run_until("load_tree \"" + cfrFilePath + "\"", "load_tree ok!")
        self.run_until("load_all_nodes", "load_all_nodes ok!")
        self.setAccuracy([self.connection.accuracy])

    def getTreeInfo(self):
        self.tryPio(self.connection.command, [""])
        
    # no args
    def getEV(self) :
        self.tryPio(self.connection.command, ["go" ])
        self.tryPio(self.connection.write_line, ["wait_for_solver"])
        self.tryPio(self.connection.wait_line, ["wait_for_solver ok!"])
        self.tryPio(self.connection.read_until_end, [])
        
        op = self.tryPio(self.connection.command, ["calc_results"])
        
        return parseEV(op)

    def getEV_partial(self, args : list) :
        nodeId = args[0]
        self.run_until("solve_partial " + nodeId, "solve_partial ok!")
        
        op = self.tryPio(self.connection.command, ["calc_results"])
        
        return parseEV(op)
    
    # arg[0] = nodeID
    def getActionFrequency(self, args : list) :
        nodeID = args[0]
        output = self.tryPio(self.connection.command, ["calc_line_freq " + nodeID])
        op = round(toFloat(output[0]), 4)
        return op
    
    
    # arg[0] = percentage
    def setAccuracy(self, args : list) :
        percent = normalizeWeight(args[0])
        pioOutput = self.tryPio(self.connection.command, ["show_tree_info"])
        if consoleLog:
            print("TREE INFO: \n")
            for p in pioOutput:
                print(p)
            print("----------------------------") 
               
        info = parseTreeInfoToMap(pioOutput)
        
        if consoleLog:
            for i in info:
                print(i)

                
        accuracy = info["Pot"] * percent
        self.tryPio(self.connection.command, ["set_accuracy " + str(accuracy)])
        
    
    # arg[0] = nodeId    
    def createSubtree(self, args : list):
        nodeID = args[0]
        t = TreeOperator(self.connection)
        
        info : nodeInfo = t.getNodeInfo(nodeID)
        oop_range, ip_range = t.getRange(nodeID)
        
        self.tryPio(self.connection.command, ["set_range OOP " + oop_range])
        self.tryPio(self.connection.command, ["set_range IP " + ip_range])
        self.tryPio(self.connection.command, ["set_pot " + info.pot])
        self.tryPio(self.connection.command, ["set_board " + info.board])
        
        self.run_until("build_tree", "build_tree ok!")
        
        
    # arg[0] = path
    def saveTree(self, args : list) :
        self.tryPio(self.connection.command, ["dump_tree \"" + args[0] + "\""])
        
        
class Tests(unittest.TestCase):
    

    
    def testgetEVs(self):
        self.connection = Solver(solverPath)
        self.pio = SolverCommmand(self.connection)
        testFiles = {"KdTc9h_small.cfr" : [36.790, 16.210] ,
                     "Qh6c5s_small.cfr" : [22.573, 30.427] ,
                     "As5h3s_small.cfr" : [28.865, 24.135]}
        for file in testFiles:
            self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\cfr\\" + file)
            oop, ip = self.pio.getEV()
            right_oop, right_ip = testFiles.get(file)
            self.assertAlmostEqual(toFloat(oop), right_oop, delta = .005)
            self.assertAlmostEqual(toFloat(ip), right_ip, delta = .005)
            
        self.connection.exit()
    

    def testSetAccuracy(self):
        self.connection = Solver(solverPath)
        self.pio = SolverCommmand(self.connection)
        self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\cfr\KdTc9h.cfr")
        
        info = parseTreeInfoToMap(self.connection.command("show_tree_info"))
        self.assertEqual(info["Pot"], 55)
        self.pio.setAccuracy([.01]) 
        settings = parseSettingsToMap(self.connection.command("show_settings"))
        self.assertEqual(settings["accuracy"], .55)
        
        self.connection.exit()
            
    def testFrequencies(self):
        self.connection = Solver(solverPath)
        self.pio = SolverCommmand(self.connection)
        
        
        nodes = ["r:0:c:b16", "r:0:c:c", "r:0:c:b16:c", "r:0:c:b16:b68", "r:0:c:b16:f"]
        testFiles = {"KdTc9h.cfr" : [.5, .5, 0.1667, 0.1667, 0.1667] ,
                     "Qh6c5s.cfr" : [.5, .5, 0.1667, 0.1667, 0.1667] ,
                     "As5h3s.cfr" : [.5, .5, 0.1667, 0.1667, 0.1667] }
        
        for file in testFiles:
            self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\cfr\\" + file)
            for i in range(0, len(nodes)):
                frequency = self.pio.getActionFrequency([nodes[i]]) 
                correct_frequency = testFiles.get(file)[i]
                self.assertAlmostEqual(frequency, correct_frequency, delta = .0001 )
            
        self.connection.exit()
    
    def Subtree(self):
        self.connection = Solver(solverPath)
        self.pio = SolverCommmand(self.connection)
        
        # load_tree "C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\cfr\KdTc9h_small.cfr"
        self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\cfr\KdTc9h_small.cfr")
        self.pio.createSubtree(["r:0:c:b16:c:3c:c:b77"])
        self.pio.saveTree([r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\cfr\KdTc9h_small_subtree.cfr"])
        # show_node r:0:c:b16:c:3c:c:b77
        # show_range OOP r:0:c:b16:c:3c:c:b77
        # show_range IP r:0:c:b16:c:3c:c:b77
        
        
        # set_range OOP 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343
        # set_range IP 0.166666657 0.166666657 0.166666672 0.166666657 0.166666672 0.166666672 0 0 0 0 0 0.166666672 0 0 0 0 0 0.166666672 0 0 0.166666672 0 0 0 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0.166666672 0 0.166666672 0 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0 0.166666672 0.166666672 0.166666672 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.166666672 0 0.166666672 0 0.166666672 0.166666672 0.166666672
        # set_pot 0 0 87
        # set_board KdTc9h3c
        
        pot = 87
        stacks = 959
        board = "KdTc9h3c"
        
    def File(self):
        
        self.maxDiff = None
        
        # range at r:0:c:b16:c
        
        OOP_range = "0 0 0 0 0 0 0.333333343 0 0 0 0 0.333333343 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343"
        IP_range = "0.5 0.5 0.5 0.5 0.5 0.5 0.5 0 0 0 0 0.5 0 0 0.5 0 0 0.5 0 0.5 0.5 0 0 0 0.5 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0 0.5 0.5 0.5"
        #OOP_range = "0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343"
        #IP_range = "0.5 0.5 0.5 0.5 0.5 0.5 0 0 0 0 0 0.5 0 0 0 0 0 0.5 0 0 0.5 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0 0.5 0.5 0.5"
        OOP_range_correct = "0 0 0 0 0 0 0.333333343 0 0 0 0 0.333333343 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343 0 0.333333343 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.333333343 0.333333343 0.333333343"
        IP_range_correct = "0.5 0.5 0.5 0.5 0.5 0.5 0.5 0 0 0 0 0.5 0 0 0.5 0 0 0.5 0 0.5 0.5 0 0 0 0.5 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0.5 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0.5 0 0.5 0.5 0.5"

        self.assertEqual(OOP_range, OOP_range_correct)
        self.assertEqual(IP_range, IP_range_correct)
        

if __name__ == '__main__': 
    unittest.main() 