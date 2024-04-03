from SolverConnection.solver import Solver
from logging_tools import parseStringToList, printList, treePath, makeString, parseNodeIDtoList, makeNodeIDfromList
from fileIO import fileReaderLocal, fileReader
from global_var import solverPath, totalCombos, sampleCFR, sampleNodeID, sampleFolder, mappingsFolder, currentdir, hand_category_index, draw_category_index, exception_categories
import unittest


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
        # format: a list of a list of 1326 floats (one per combo)
        strategy = self.getCurrentStrategyAsList(parentID)

        
        
        self.alter_strategy(strategy, weightMap, targetIndex, targetNodeID)
        
        # set the new target strategy in the original pio output 
        strategy = self.strategyListToString(strategy)
        
        self.connection.command("set_strategy " + parentID + " " + strategy)
        
        self.connection.command("lock_node " + parentID) 
    
    
    
    def getCurrentStrategyAsList(self, nodeID: str) -> list[list[float]] :
        strategy = self.connection.command("show_strategy " + nodeID)
        # turn each individual strategy (string) in the list into a list of numbers
        return self.strategyStringToList(strategy) 


    def strategyStringToList (self, strategy : list[str]) -> list[list[float]] :
        for i in range(0,len(strategy)):
            strategy[i] = parseStringToList(strategy[i])
        return strategy

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
        op = self.connection.command("show_categories " + self.getBoard(nodeID))
        # a 1326 length list of integers, each referencing the hand category the corresponding combo belongs to.
        hand_per_combo = parseStringToList(op[0])
        draw_per_combo = parseStringToList(op[1])
        return [hand_per_combo, draw_per_combo]

    # checks if category is draw or hand category and updates weights accordingly
    def alter_strategy(self, strategy : list[list[float]], weightMap : dict[str, int], targetIndex: int, targetNodeID : str) -> list[float]:

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

    # when entering in weights in JSTON, could be decimal or percentage. 
    # this taccounts for inconsistency in human entry (20% could be typed in as .2 or 20)
    def normalizeWeight(self, weight_in_JSON: float) -> float:
        if (weight_in_JSON > 1):
                weight_in_JSON = weight_in_JSON/100
        return weight_in_JSON
    
    # alters the combos that belong to the given category to the given weight
    # updates the corresponding combos in the other child nodes to a weight that keeps the proportions of the other strategies the same as before
    def update_weight(self, strategy : list[list[float]], targetIndex : int, categoriesOfCombos : list[int], category : int, newWeight : float, addWeight : bool) -> list[float]:
        for comboIndex in range(0,totalCombos):
            # if the category of the combo in the target node is equal to the category whose weight we are trying to change
            if categoriesOfCombos[comboIndex] == category:
                
                oldWeight = strategy[targetIndex][comboIndex]
            
                newWeight = self.normalizeWeight(newWeight)
                    
                #if addWeight:
                    #newWeight = oldWeight + newWeight
                    
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


sampleConnection = Solver(solverPath)
samplePath = treePath(sampleCFR)
sampleWeightsFile = currentdir + sampleFolder + "weights.json"
    
sampleConnection.command("load_tree " + samplePath)
sampleConnection.command("load_all_nodes")

nodelocker = NodeLocker(sampleConnection)
        
comboWeights = fileReader.JSONtoMap(sampleWeightsFile)
comboIndexes = fileReaderLocal.JSONtoMap(mappingsFolder + "handIndexMap")

        
class Tests(unittest.TestCase):
    
        
    def testNodelocking(self):
        comboWeights = fileReader.JSONtoMap(sampleWeightsFile)
        comboIndexes = fileReaderLocal.JSONtoMap(mappingsFolder + "handIndexMap")
        
        self.assertEqual(list(comboWeights.keys()), ["king_high", "bdfd_2card"])
        
        nodeInfo = nodelocker.get_parent_and_id_of_targetNode(sampleNodeID)
        parentID = nodeInfo[0]
        targetIndex = nodeInfo[1]
        
        self.assertEqual(parentID, "r:0:c")
        
        oldStrategy = nodelocker.getCurrentStrategyAsList(parentID)
        
        for s in oldStrategy:
            self.assertEqual(len(s), totalCombos)
            self.assertEqual(s[0], 0.5)
        
        nodelocker.set_strategy(sampleWeightsFile, sampleNodeID)
        
        finalStrategy = nodelocker.getCurrentStrategyAsList(parentID)
        
        king_high_index = comboIndexes.get("KsQs")
        bd_2_index = comboIndexes.get("AhKh")
        
        king_high_correct_weight = nodelocker.normalizeWeight(comboWeights.get("king_high"))
        #bd_2_correct_weight =  oldStrategy[targetIndex][bd_2_index] + nodelocker.normalizeWeight(comboWeights.get("bdfd_2card"))
        bd_2_correct_weight = nodelocker.normalizeWeight(comboWeights.get("bdfd_2card"))
        
        #printList(finalStrategy)
        
        self.assertAlmostEqual(finalStrategy[targetIndex][king_high_index], king_high_correct_weight)
        self.assertAlmostEqual(finalStrategy[1-targetIndex][king_high_index], 1 - king_high_correct_weight)
        self.assertAlmostEqual(finalStrategy[targetIndex][bd_2_index], bd_2_correct_weight)
        self.assertAlmostEqual(finalStrategy[1-targetIndex][bd_2_index], 1 - bd_2_correct_weight)
        

if __name__ == '__main__': 
    unittest.main()