
from __future__ import annotations
from stringFunc import parseEV, toFloat, parseTreeInfoToMap, parseSettingsToMap
import unittest
from global_var import solverPath
from SolverConnection.solver import Solver


def normalizeWeight(n: float) -> float:
        if (n > 1):
               n = n/100
        return n
# functions that transmit commands to the solver to get correct output
class SolverCommmand():
    def __init__(self, connection) -> None:
        self.connection = connection
    
    def tryPio(self, func , args : list): 
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
        
    def load_tree(self, cfrFilePath) :
        self.tryPio(self.connection.command, ["load_tree \"" + cfrFilePath + "\""])
        self.tryPio(self.connection.command, ["load_all_nodes"])
        self.setAccuracy([.01])


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
    
    # arg[0] = nodeID
    def getActionFrequency(self, args : list) :
        nodeID = args[0]
        output = self.tryPio(self.connection.command, ["calc_line_freq " + nodeID])
        op = round(toFloat(output[0]), 4)
        print(op)
        return op
    
    
    # arg[0] = percentage
    def setAccuracy(self, args : list) :
        percent = normalizeWeight(args[0])
        info = parseTreeInfoToMap(self.tryPio(self.connection.command, ["show_tree_info"]))
        accuracy = info["Pot"] * percent
        self.tryPio(self.connection.command, ["set_accuracy " + accuracy])
        
    # arg[0] = path
    def saveTree(self, args : list) :
        self.tryPio(self.connection.command, ["dump_tree \"" + args[0] + "\""])
        
        
class Tests(unittest.TestCase):
    
    def testGetEVs(self):
        self.connection = Solver(solverPath)
        self.pio = SolverCommmand(self.connection)
        
        
        testFiles = {"KdTc9h_small.cfr" : [36.790, 16.210] ,
                     "Qh6c5s_small.cfr" : [22.573, 30.427] ,
                     "As5h3s_small.cfr" : [28.865, 24.135]}
        for file in testFiles:
            self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\\" + file)
            oop, ip = self.pio.getEV()
            right_oop, right_ip = testFiles.get(file)
            self.assertAlmostEqual(toFloat(oop), right_oop, delta = .005)
            self.assertAlmostEqual(toFloat(ip), right_ip, delta = .005)
            
        self.connection.exit()

    def testSetAccuracy(self):
            self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\\KdTc9h_small.cfr")
            info = parseTreeInfoToMap(self.connection.command("show_tree_info"))
            self.assertEqual(info["Pot"], 55)
            self.pio.setAccuracy([.01]) 
            settings = parseSettingsToMap(self.connection.command("show_settings"))
            self.assertEqual(settings["accuracy"], .55)
            
    def testFrequencies(self):
        self.connection = Solver(solverPath)
        self.pio = SolverCommmand(self.connection)
        
        
        nodes = ["r:0:c:b16", "r:0:c:c", "r:0:c:b16:c", "r:0:c:b16:b68", "r:0:c:b16:f"]
        testFiles = {"KdTc9h_small.cfr" : [.5, .5, 0.1667, 0.1667, 0.1667] ,
                     "Qh6c5s_small.cfr" : [.5, .5, 0.1667, 0.1667, 0.1667] ,
                     "As5h3s_small.cfr" : [.5, .5, 0.1667, 0.1667, 0.1667] }
        
        for file in testFiles:
            self.pio.load_tree(r"C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\\" + file)
            for i in range(0, len(nodes)):
                frequency = self.pio.getActionFrequency([nodes[i]]) 
                correct_frequency = testFiles.get(file)[i]
                self.assertAlmostEqual(frequency, correct_frequency, delta = .0001 )
            
        self.connection.exit()
    
    
            
if __name__ == '__main__': 
    unittest.main() 