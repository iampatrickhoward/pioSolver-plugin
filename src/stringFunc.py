from __future__ import annotations
from errorMessages import Errors
import unittest
from datetime import datetime
from decimal import Decimal



# this file has scripts that parse dat from one format to another

def timestamp():
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

def toFloat(string :str):
    try:
        return Decimal(string)
    except Exception:
        return string

def parseStringToList(strOutput : str) -> list[str]:
    # delimit pioSolver output using whitespace
    output : list[str] = strOutput.split(" ")
    # strip of colons and additional whitespace
    for i in range(0, len(output)):
        output[i] = output[i].strip()
        output[i] = toFloat(output[i])
    return output


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


def parseTreeInfoToMap (info : list[str]) -> dict[str, any] :
    map = {}
    for i in info:
        # #FlopConfig.RaiseSize#60
        pair = i.split("#")
         # ['', 'FlopConfig.RaiseSize', '60']
        try:
            map[pair[1]] = toFloat(pair[2])
        except Exception:
            print("entry is " + str(pair[2]))
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
        pair = s.split(":")
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
    
    def testToDecimal(self):
        str = ".000005"
        self.assertEqual(toFloat(str) - Decimal(str), 0)
        self.assertEqual(toFloat("neegus"), "neegus")

if __name__ == '__main__': 
    unittest.main() 