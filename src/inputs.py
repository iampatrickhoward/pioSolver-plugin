from enum import Enum
from global_var import hand_category_index, draw_category_index, exception_categories, sampleFolder
from fileIO import fileWriter, fileReader, fileReaderLocal
from logging_tools import parseNodeIDtoList, toFloat
from errorMessages import Errors
import os
import unittest

class Extension (Enum):
    cfr = ".cfr"
    csv = ".csv"
    json = ".json"
    # folders have no extension
    folder = ""

class InputType (Enum):
    file = 1
    number = 2
    text = 3
    
# an input needed by the user, with accompanying prompt
class Input ():
    def __init__(self, type : InputType, prompt : str) :
        self.prompt = prompt
        self.type = type
            
    # checks if is valid input
    def isValid (self, input: str) -> bool:
        return True
    
    def readInput (self, input: str):
        if self.isValid(input) :
            return input

# a file input with specific extension or extensions needed from the user
class FileInput (Input):
    def __init__(self, extension : Extension, prompt : str):
        super().__init__(InputType.file, prompt)
        self.extension : str = extension.value
    
    def isCorrectExtension (self, fName : str) :
        # if last few letters of file name equals the extension this input is supposed to have, return true
        if (fName[-1*len(self.extension):]) == self.extension:
                return True
        return False
    
    # check if file type is correct, if so return
    def readInput(self, input : str) :
        if self.isCorrectExtension(input):
            return input
        raise Exception(Errors.wrongFileType(self.extension))


class FolderOf (FileInput) :

    
    def __init__(self, extension: Extension, prompt: str):
        super().__init__(extension, prompt)
    
    # check if file type is correct, if so return
    def readInput(self, input : str) -> list[str] :
        allFilesInside : list [str] = []
        try: 
            allFilesInside = os.listdir(input)
        except: 
            raise Exception(Errors.invalidFolder)
        neededFiles = []
        # return the files inside the folder which match the needed extension
        for f in allFilesInside:
            if self.isCorrectExtension(f):
                neededFiles.append(f)
        if not neededFiles:
            raise Exception(Errors.invalidFolder + Errors.noFilesinFolder(self.extension))
        return neededFiles
    
class WeightsFile (FileInput):
    def __init__(self, prompt: str):
        super().__init__(Extension.json, prompt)
    
    # input: a file path from the interface
    # output: a map of valid category names and their corresponding weights
    def readInput(self, input : str) -> dict[str, int] :
        input = super().readInput(input)
        weightMap : dict = fileReader.JSONtoMap(input)
        
        for category_name in weightMap:
            validName : bool = category_name in hand_category_index or category_name in draw_category_index
            if not validName:
                raise Exception(Errors.invalidCategory(category_name))
            weight = toFloat(str(weightMap.get(category_name)))
            
            if weight < 0 and category_name not in exception_categories:
                raise Exception(Errors.noNegativeWeights(category_name))
        return weightMap

class Decisions(Enum):
        ROOT = "r:0"
        CHECK = "c"
        # a bet where the size is constant
        BET_SIZE = "b"
        # a bet where the size is file specific
        BET = "bet"
        TURN = "turn"
        RIVER = "river"
        
        @staticmethod
        def getDict():
            return {i.value: i for i in Decisions}
        
class BoardFile(FileInput):

    decisionDict = Decisions.getDict()
    
    def __init__(self, prompt: str):
        super().__init__(Extension.json, prompt)
        
    # input: a file path from the interface
    # output: a map of cfr file names and their corresponding target nodeIDs
    def readInput(self, input : str) -> dict[str, str] :
        input = super().readInput(input)
        
        board = fileReader.JSONtoMap(input)
        nodeID = board.get("all")
        if nodeID is None:
            raise Exception (Errors.noDecisionLineError)

        if (len(board) == 1) :
            return BoardFile.hasNoSpecificDecisions(nodeID)
        else:
            board.pop("all")
            # board has only specific file info
            return BoardFile.getSpecificNodeIDs(nodeID, board)

            
        
        
    
    
    @staticmethod
    # checks that there are no decisions that require specifices in one line boards
    def hasNoSpecificDecisions (nodeID : str) -> str: 
        decisions = BoardFile.makeDecisionList(nodeID)
        
        for d in decisions:
            if d in [Decisions.BET, Decisions.TURN, Decisions.RIVER]:
                # append the following 
                raise Exception(Errors.needsSpecificFileInfo)
        return nodeID

    
    @staticmethod
    # get the node IDs for each .cfr file 
    def getSpecificNodeIDs (nodeID: str, board : dict) -> dict [str : str]: 
        #add all file names to a new dictionary
        nodeIDPerFile = {}
        for b in board:
            nodeIDPerFile[b] = ""
        
        decisions = BoardFile.makeDecisionList(nodeID)
        
  
        for n in nodeIDPerFile:
            for d in decisions:
                # if the decision is one of these
                if d in [Decisions.ROOT, Decisions.CHECK]:
                    # append the following 
                    nodeIDPerFile[n] = nodeIDPerFile[n] + d.value + ":"
                if d == Decisions.BET_SIZE:
                    nodeIDPerFile[n] = nodeIDPerFile[n] + d.value 
                elif type(d) is str:
                    nodeIDPerFile[n] = nodeIDPerFile[n] + d + ":"
                elif d in [Decisions.TURN, Decisions.RIVER]: 
                    move = board.get(n).pop(0)
                    nodeIDPerFile[n] = nodeIDPerFile[n] + move + ":"
                elif d in [Decisions.BET]:
                    move = board.get(n).pop(0)
                    if not move.isnumeric():
                        raise Exception(Errors.nonNumericBetError)
                    nodeIDPerFile[n] = nodeIDPerFile[n] + "b" + move + ":"
             # remove extraneous : at end
            nodeIDPerFile[n] = nodeIDPerFile[n][:-1]
       
        return nodeIDPerFile
        
        
    
            
    @staticmethod
    def makeDecisionList(node: str) -> list[Decisions]:
        nodes = parseNodeIDtoList(node)
        decisionList : list[Decisions]= []
        
        for n in nodes :
            x = BoardFile.getDecisionType(n)
            if (x):
                decisionList.append(x)
            if (x == Decisions.BET_SIZE):
                # if it's a bet with size, append the size of the bet
                decisionList.append(n[1:])
        
        if len(decisionList) == 0 or decisionList[0] != Decisions.ROOT:
            raise Exception(Errors.noRootError)
        
        return decisionList
    
    @staticmethod
    def getDecisionType(node : str):
        if node == "r:0":
            return Decisions.ROOT
        first = node[:1]
        if first == "c" and (len(node) == 1):
            return Decisions.CHECK
        if first == "b":
            if  (len(node) == 1) :
                return Decisions.BET
            elif node[1:].isnumeric() : 
                return Decisions.BET_SIZE
        if node == "turn" :
            return Decisions.TURN
        if node == "river" :
            return Decisions.RIVER
        
        raise Exception(Errors.invalid_node(node))
        
        



class Tests(unittest.TestCase):
    
    def testMakeDecisionList(self):
        self.assertEqual(BoardFile.makeDecisionList("r:0"), [Decisions.ROOT])
        try:
            BoardFile.makeDecisionList("p")
        except Exception as e:
            self.assertEqual(str(e), Errors.invalid_node("p"))
        try:
            BoardFile.makeDecisionList("c:c:b15")
        except Exception as e:
            self.assertEqual(str(e), Errors.noRootError)
        try:
            BoardFile.makeDecisionList("r")
        except Exception as e:
            self.assertEqual(str(e), Errors.invalid_node("r"))
            
        self.assertEqual(BoardFile.makeDecisionList("r:0:c"), [Decisions.ROOT, Decisions.CHECK])
        self.assertEqual(BoardFile.makeDecisionList("r:0:c:c"), [Decisions.ROOT, Decisions.CHECK, Decisions.CHECK])
        self.assertEqual(BoardFile.makeDecisionList("r:0:c:c:turn"), [Decisions.ROOT, Decisions.CHECK, Decisions.CHECK, Decisions.TURN])
        self.assertEqual(BoardFile.makeDecisionList("r:0:c:c:b12"), [Decisions.ROOT, Decisions.CHECK, Decisions.CHECK, Decisions.BET_SIZE, "12"])
        self.assertEqual(BoardFile.makeDecisionList("r:0:c:c:b"), [Decisions.ROOT, Decisions.CHECK, Decisions.CHECK, Decisions.BET])
        
    
    def testWeightFile(self):
        w = WeightsFile("Enter a weights file.")
        w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "weights.json"))
        
    def testFolder(self):
        w = FolderOf(Extension.cfr, "Select a folder with .cfr files")
        files = w.readInput(fileReaderLocal.getLocalPath(sampleFolder))
        self.assertEqual(files, ['As5h3s.cfr', 'KdTc9h.cfr', 'Qh6c5s.cfr'])
        
        try:
            w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "weights.json"))
        except Exception as e:
            self.assertEqual(str(e), Errors.invalidFolder)
            
        try:
            w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "folder"))
        except Exception as e:
            self.assertEqual(str(e), Errors.invalidFolder + "Folder has no " + w.extension + " files. ")
    
    def testBoardFile(self):
        
        
        w = BoardFile("Enter a board file.")
        self.assertEqual(BoardFile.decisionDict, {"r:0" : Decisions.ROOT, 
                                                  "c" : Decisions.CHECK,
                                                  "b" : Decisions.BET_SIZE,
                                                  "bet" : Decisions.BET,
                                                  "turn" : Decisions.TURN,
                                                  "river" : Decisions.RIVER})
        try:
            w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "board_bad.json"))
        except Exception as e:
            self.assertEqual(str(e),Errors.noRootNode)

        o = w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "board_turn.json"))
        self.assertEqual(o, {"As5h3s" : "r:0:c:c:Ah:c",
                             "KdTc9h" : "r:0:c:c:Ts:c",
                             "Qh6c5s" : "r:0:c:c:Ts:c"})
        
        o = w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "board_simple.json"))
        self.assertEqual(o, "r:0:c:c:b10")
        
        try:
            o = w.readInput(fileReaderLocal.getLocalPath(sampleFolder + "board_bad.json"))
        except Exception as e:
            self.assertEqual(str(e), Errors.noRootNode)
        
        o = BoardFile.getSpecificNodeIDs("r:0:c:c:turn:b10:b:river",
                                         {"cfr1" : ["Ah", "15" , "Ts"],
                                          "cfr2" : ["Ah", "10" , "Kh"]},
                                         )
        self.assertEqual(o, {"cfr1" : "r:0:c:c:Ah:b10:b15:Ts",
                             "cfr2" : "r:0:c:c:Ah:b10:b10:Kh"})
        
if __name__ == '__main__': 
    unittest.main() 