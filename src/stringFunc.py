from SolverConnection.solver import Solver
import re
from errorMessages import Errors
from global_var import currentdir
import unittest
from datetime import datetime
from __future__ import annotations


# this file has scripts that parse dat from one format to another

def timestamp():
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

def toFloat(string :str):
    try:
        return float(string)
    except ValueError:
        return string

def getDirectoryofFile(fName : str) -> str:
    path : list[str] = fName.split("\\")
    path = path[:-1]
    dir =  ""
    for p in path:
        dir = dir + p + "\\"
    return dir

def parseStringToList(strOutput : str) -> list[str]:
    # delimit pioSolver output using whitespace
    output : list[str] = strOutput.split(" ")
    # strip of colons and additional whitespace
    for i in range(0, len(output)):
        output[i] = output[i].strip()
        output[i] = toFloat(output[i])
    return output

def printList (lst):
    print("------------------------------")
    for i in lst:
        print(i)
    print("------------------------------")

# encloses a string in quotes. this is how file names need to be give to Pio
def inQuotes (string : str) -> str:
    return "\"" + string + "\""

def treePath (fName: str) -> str:
    return inQuotes(currentdir + fName + ".cfr")

def removeExtension(file: str) -> str:
    return file.split(".")[0]


#---------------------------------------------pio outputs to data---------------------------------------#

def parseEV(results: list[str]) -> list[str]:
    values = []
    for r in results:
        label, value = r.split(":")
        if label in ["EV OOP", "EV IP"]:
            values.append(value)
    return values

# node IDs are in the form r:0:c:c:
def parseNodeIDtoList(nodeID : str) -> list[str]:
    nodes : list [str] = nodeID.split(":")
    if len(nodes) < 2:
        raise Exception(Errors.invalid_node(nodeID))
    if nodes[0] == "r" and nodes[1] == "0":
        nodes.pop(0)
        nodes[0] = "r:0"
    return nodes

def parseStrategyToList (strategy : list[str]) -> list[list[float]] :
    for i in range(0,len(strategy)):
        strategy[i] = parseStringToList(strategy[i])
    return strategy

#Example Output
#Type#NoLimit
#Range0#AA,KK,JJ,TT,88,77,66,55,KQo,QJo,T9o,98o,87o,76s,65s,54s,43s,32s
#Range1#AA,KK,44,33,22,AKo,KQo,QTo,T8o,87o,76o,65o,54o,32s
#Rake.Enabled#True
#Rake.Fraction#0.05
#Rake.Cap#2
#Board#Kd Tc 9h
#Pot#55
#EffectiveStacks#975
#AllinThreshold#67
#AddAllinOnlyIfLessThanThisTimesThePot#300
#UnifiedBetAfterRaise#70
#UseUnifiedRaiseAfterRaise#True
#UnifiedRaiseAfterRaise#45
#FlopConfig.RaiseSize#60
#TurnConfig.BetSize#70
#TurnConfig.RaiseSize#60
#RiverConfig.BetSize#70
#RiverConfig.RaiseSize#60
#RiverConfig.AddAllin#True
#FlopConfigIP.BetSize#30
#FlopConfigIP.RaiseSize#60
#TurnConfigIP.BetSize#70, 150
#TurnConfigIP.RaiseSize#60
#RiverConfigIP.BetSize#70
#RiverConfigIP.RaiseSize#60
#RiverConfigIP.AddAllin#True

def parseTreeInfoToMap (info : list[str]) -> dict[str, any] :
    map = {}
    for i in info:
        pair = i.split("#")
        map[pair[0]] = toFloat(pair[1])
    return map

'''
show_settings
accuracy: 0.000000
accuracy mode: chips
thread_no: 0
info_freq: 0
step: 1.000000
hopeless_thres: 0.200000
adjust_mode: 1
recalc_accuracy: 0.002500 0.001000 0.000500
isomorphism: 1 0
ignore mememory check: 0
'''

def parseSettingsToMap(settings : list[str]) -> dict[str, any]:
    map = {}
    for s in settings:
        pair = i.split(":")
        map[pair[0]] = toFloat(pair[1])
    return map
#--------------------------------------------data to pio input---------------------------------------#

def makeNodeIDfromList(nodes : list[str]) -> str:
    list = ""
    for n in nodes:
        list = list + ":" + n
    return list[1:]

# turns list into a string to feed into Pio
def makeString(elems : list[type]) -> str:
    strInput : str = ""
    for i in elems:
        strInput = strInput + i.__str__() + " "
    #removes whitespace at end
    return strInput[0: len(strInput) - 1]

def makeStrategyFromList(strategy : list[list[float]]) -> list[str] :
    for i in range(0,len(strategy)):
        strategy[i] = makeString(strategy[i])
    return makeString(strategy)
    


class Tests(unittest.TestCase):
    
    def testInQuotes(self):
        self.assertEqual(inQuotes("hi"), "\"hi\"")
        
    def testStringToList(self):
        self.assertEqual(toFloat("0.5"), 0.5)
        self.assertEqual(toFloat("05"), 5.0)
        s = '0.5 0.5'
        list = parseStringToList(s)
        self.assertEqual(list, [0.5, 0.5])
        
    def testListToString(self):
        string = makeString([1, 2, 3])
        self.assertEqual(string, "1 2 3")
        
    def testNodeToListConversion(self):
        nodeID = "r:0:c:c:b25:turn"
        nodeList = parseNodeIDtoList(nodeID)
        nodeIDagain = makeNodeIDfromList(nodeList)
        self.assertEqual(nodeList, ["r:0", "c", "c", "b25", "turn"])
        self.assertEqual(nodeID, nodeIDagain)

if __name__ == '__main__': 
    unittest.main() 