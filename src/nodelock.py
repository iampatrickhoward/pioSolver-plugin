from SolverConnection.solver import Solver
from logging_tools import parseStringToList, printList, treePath, makeString, parseNodeIDtoList, makeNodeIDfromList
from fileIO import fileReaderLocal, fileReader
from global_var import solverPath, totalCombos, sampleCFR, sampleNodeID, sampleFolder, mappingsFolder
import unittest


sampleConnection = Solver(solverPath)
samplePath = treePath(sampleCFR)
sampleWeightsFile = sampleFolder + "weights"
    
sampleConnection.command("load_tree " + samplePath)
sampleConnection.command("load_all_nodes")


class NodeLocker(): 
    def __init__(self, connection):
        self.connection = connection
        
        
    def set_strategy(self, weightsFile, targetNodeID) :
        
        #makeMappings()
        
        
        weightMap = fileReader.JSONtoMap(weightsFile)
        
        targetNodeInfo = self.get_parent_and_id_of_targetNode(targetNodeID)
        
        parentID = targetNodeInfo[0]
        targetIndex = targetNodeInfo[1]
        
        self.connection.command("unlock_node " + parentID) 
        
        # the strategy map of the target node and all its sister node
        # format: a list of strings, each having 1326 floats (one per combo)
        strategy = self.connection.command("show_strategy " + parentID) 
        
        # turn each strategy into a list of numbers
        self.strategyStringToList(strategy)
        
        #printList(strategy)
        
        self.alter_strategy(strategy, weightMap, targetIndex, targetNodeID)
        
        # set the new target strategy in the original pio output 
        strategy = self.strategyListToString(strategy)
        
        self.connection.command("set_strategy " + parentID + " " + strategy)
        
        self.connection.command("lock_node " + parentID) 
    
    
        


    def strategyStringToList (self, strategy : list[str]) -> list[list[float]] :
        for i in range(0,len(strategy)):
            strategy[i] = parseStringToList(strategy[i])

    def strategyListToString (self, strategy : list[list[float]]) -> list[str] :
        for i in range(0,len(strategy)):
            strategy[i] = makeString(strategy[i])
            #print(strategy[i])
        return makeString(strategy)


    # in order to nodelock a particular decision, we need to reference it by its index number as the child of the parent
    # this takes a node and returns both in the form [parentNodeID, index]
    def get_parent_and_id_of_targetNode(self, targetNodeID: str) -> tuple[str : int]:
        nodes = parseNodeIDtoList(targetNodeID)
        # remove last decision to get parents
        nodes.pop()
        parentNode = makeNodeIDfromList(nodes)
        allChildIDs = self.getChildIDs(parentNode)
        index = 0
        for id in allChildIDs:
            if id == targetNodeID:
                return [parentNode, index]
            index = index + 1
        raise Exception("Invalid decision node")
        
        


    def getChildIDs (self, nodeID : str) -> list[str] :
        # example output: 
        # ['child 0:', 'r:0:c:b16', 'OOP_DEC', 'As 5h 3s', '0 16 55', '3 children', 'flags: PIO_CFR', '', 'child 1:', 'r:0:c:c', 'SPLIT_NODE', 'As 5h 3s', '0 0 55', '49 children', 'flags:', '']
        output = self.connection.command("show_children " + nodeID) 
        childList = []
        child = []
        ids = []
        # split single list into list of lists using delimiter ''
        for o in output:
            if (o == ''):
                childList.append(child)
                child = []
            else:
                child.append(o)
                
        for c in childList:
            ids.append(c[1])
        
        return ids

    # gets the board at the current node in a format that can be fed to other commands
    def getBoard(self, nodeID : str) -> str:
        # example output: ['r:0:c', 'IP_DEC', 'As 5h 3s', '0 0 55', '2 children', 'flags: PIO_CFR', '']
        op : list[str] = self.connection.command("show_node " + nodeID)
        # remove whitespace from board
        board : str = op[2].replace(" ", "")
        # format As5h3s
        return board

        
    def parseCategories(self, nodeID):
        op = self.connection.command("show_categories " + getBoard(nodeID))
        # a 1326 length list of integers, each referencing the hand category the corresponding combo belongs to.
        hand_per_combo = parseStringToList(op[0])
        draw_per_combo = parseStringToList(op[1])
        return [hand_per_combo, draw_per_combo]

    # checks if category is draw or hand category and updates weights accordingly
    def alter_strategy(self, strategy : list[list[float]], weightMap : dict[str, int], targetIndex: int, targetNodeID : str) -> list[float]:
        # format: {"nothing": 0, "king_high": 1, "ace_high": 2, "low_pair": 3...
        
        hand_category_index = fileReaderLocal.JSONtoMap(mappingsFolder + "hand_categories")
        # format: {"no_draw": 0, "bdfd_1card": 1, "bdfd_2card": 2, ...
        draw_category_index = fileReaderLocal.JSONtoMap(mappingsFolder + "draw_categories")
        
        # there are certain draw categories where the weight inputted by the user is meant to be added to the original weight rather than replacing it
        exception_categories = fileReaderLocal.JSONtoMap(mappingsFolder + "exception_categories")
        
        # derives the hand and draw categories (their indexes) of combos in target node from pio output
        target_categories = self.parseCategories(targetNodeID)
        target_hand_cats= target_categories[0]
        target_draw_cats = target_categories[1]
        
        for category_name in weightMap:
            # if it is a hand category
            addInsteadOfReplace = False
            if category_name in exception_categories:
                addInsteadOfReplace = True
            if category_name in hand_category_index:
                # inputs: the current strategy, the index of the target node, the category index corresponding to the category name, the weight of that category)
                strategy = self.update_weight(strategy, targetIndex, target_hand_cats, hand_category_index.get(category_name), weightMap.get(category_name), addInsteadOfReplace)
            # if it is a draw category
            if category_name in draw_category_index:
                strategy = self.update_weight(strategy, targetIndex, target_draw_cats, draw_category_index.get(category_name), weightMap.get(category_name), addInsteadOfReplace)

    # alters the combos that belong to the given category to the given weight
    # updates the corresponding combos in the other child nodes to a weight that keeps the proportions of the other strategies the same as before
    def update_weight(self, strategy : list[list[float]], targetIndex : int, categoriesOfCombos : list[int], category : int, newWeight : float, addWeight : bool) -> list[float]:
        for comboIndex in range(0,totalCombos):
            # if the category of the combo in the target node is equal to the category whose weight we are trying to change
            if categoriesOfCombos[comboIndex] == category:
                
                oldWeight = strategy[targetIndex][comboIndex]
            
                # when entering in weights, could be decimal or percentage. account for inconsistency in human entry (20% could be typed in as .2 or 20)
                if (newWeight > 1):
                    newWeight = newWeight/100
                    
                if addWeight:
                    newWeight = oldWeight + newWeight
                    
                    if newWeight < 0:
                        raise Exception("Weight adjustment entered is invalid; cannot have negative percentage")
                
                # this is constant that, multiplied by the weight of the other nodes, will maintain their relative proportions
                k = (1 - newWeight)/(1 - oldWeight)
                
                # iterate through all child nodes
                for childIndex in range(0,len(strategy)) :
                    if childIndex == targetIndex:
                        strategy[childIndex][comboIndex] = newWeight
                    else :
                        strategy[childIndex][comboIndex] = round(strategy[childIndex][comboIndex] * k, 7)
        return strategy


        
class Tests(unittest.TestCase):

    def __init__(self, methodName: solverPath = "runTest") -> None:
        super().__init__(methodName)
        
        self.sampleConnection = Solver(solverPath)
        self.samplePath = treePath(sampleCFR)
        self.sampleWeightsFile = sampleFolder + "weights"
    
        self.sampleConnection.command("load_tree " + samplePath)
        self.sampleConnection.command("load_all_nodes")
        self.nodelocker = NodeLocker(sampleConnection)
        
        self.comboWeights = fileReaderLocal.JSONtoMap(self.sampleWeightsFile)
        
        
    def testReadWeightMap(self):
        self.assertEqual(list(self.comboWeights.keys()), ["king_high", "bdfd_2card"])
        
    def testParseCategories(self):
        printList(self.nodelocker.parseCategories(sampleNodeID))
        
    def testNodeLocking(self):
        self.nodelocker.set_strategy(self.sampleWeightsFile, sampleNodeID)
        
        nodeInfo = self.nodelocker.get_parent_and_id_of_targetNode()
        parentID = nodeInfo[0]
        index = nodeInfo[1]
        
        finalStrategy = self.connection.command("show_strategy " + parentID)
        
        
    
        

if __name__ == '__main__': 
    unittest.main()