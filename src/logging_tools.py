from SolverConnection.solver import Solver
import re
from errorMessages import Errors
from global_var import currentdir
import unittest

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

def parseOutputToList(strOutput : str) -> list[str]:
    # delimit pioSolver output using whitespace
    output : list[str] = strOutput.split("  ")
    # strip of colons and additional whitespace
    for i in range(0, len(output)):
        output[i] = output[i].strip(": ")
        output[i] = toFloat(output[i])
    return output

def parseStringToList(strOutput : str) -> list[str]:
    # delimit pioSolver output using whitespace
    output : list[str] = strOutput.split(" ")
    # strip of colons and additional whitespace
    for i in range(0, len(output)):
        output[i] = output[i].strip()
        output[i] = toFloat(output[i])
    return output

def parseResults(results: list[str]) -> dict[str:str]:
    evs = {}
    for r in results:
        pair : list[str] = r.split(":")
        evs[pair[0]] = pair[1]
    return evs

# node IDs are in the form r:0:c:c:
def parseNodeIDtoList(nodeID : str) -> list[str]:
    nodes : list [str] = nodeID.split(":")
    if len(nodes) < 2:
        raise Exception(Errors.invalid_node(nodeID))
    if nodes[0] == "r" and nodes[1] == "0":
        nodes.pop(0)
        nodes[0] = "r:0"
    return nodes

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