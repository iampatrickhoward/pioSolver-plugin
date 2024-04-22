from SolverConnection.solver import Solver
from stringFunc import parseStringToList, printList, treePath, makeString, parseNodeIDtoList, makeNodeIDfromList, strategyListToString, makeStrategyFromList
from fileIO import fileReaderLocal, fileReader
from global_var import solverPath, totalCombos, sampleCFR, sampleNodeID, sampleFolder, mappingsFolder, currentdir, hand_category_index, draw_category_index, exception_categories
import unittest

printConsole = False

class TreeOperator(): 
    def __init__(self, connection, nodeID = "r:0:c"):
        self.connection = connection
        if self.connection.command("is_tree_present") == "false":
            raise Exception("No tree is loaded; cannot perform tree operations")
            
        self.nodeID = nodeID
        # sets the parent, sisters, and index fot he target node
        self.get_family()
        self.children = self.getChildIDs(nodeID)
    
    
    
    # args[0] weightsFile
    def set_strategy(self, args : list) :
        #makeMappings()
        weightMap = args[0]
        
        self.connection.command("unlock_node " + self.parent) 
        
        # the strategy map of the target node and all its sister nodeq
        # format: a list of a list of 1326 floats (one per combo)
        strategy = self.getCurrentStrategyAsList(self.parent)

        
        self.alter_strategy(strategy, weightMap, self.nodeIndex, self.nodeID)
        
        # set the new target strategy in the original pio output 
        strategy = strategyListToString(strategy)
        
        self.connection.command("set_strategy " + self.parent + " " + strategy)
        
        self.connection.command("lock_node " + self.parent) 
    
    
    
    def getCurrentStrategyAsList(self, nodeID: str) -> list[list[float]] :
        strategy = self.connection.command("show_strategy " + nodeID)
        # turn each individual strategy (string) in the list into a list of numbers
        return makeStrategyFromList(strategy) 


    # in order to nodelock a particular decision, we need to reference it by its index number as the child of the parent
    # this takes a node and returns both in the form [parentNodeID, [sister node IDs], index]
    def get_family(self):
        nodes = parseNodeIDtoList(self.nodeID)
        # remove last decision to get parents
        nodes.pop()
        # turn list back into ID
        self.parent = makeNodeIDfromList(nodes)
        self.sisters = self.getChildIDs(self.parent)
        index = 0
        for id in self.sisters:
            if id == self.nodeID:
                self.nodeIndex = index
                return
            index = index + 1
            
        error = "Invalid decision node - the child nodes of " + self.parent + " are: "
        for id in self.sisters:
            error = error + " " + id
        raise Exception(error)
        
        


    def getChildIDs (self, nodeID : str) -> list[str] :
        # example output: 
        # ['child 0:', 'r:0:c:b16', 'OOP_DEC', 'As 5h 3s', '0 16 55', '3 children', 'flags: PIO_CFR', '', 'child 1:', 'r:0:c:c', 'SPLIT_NODE', 'As 5h 3s', '0 0 55', '49 children', 'flags:', '']
        output = self.connection.command("show_children " + nodeID) 
        if printConsole:
            print (output)
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
            addInsteadOfReplace = category_name in exception_categories
            
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
        newWeight = self.normalizeWeight(newWeight)
        for comboIndex in range(0,totalCombos):
            # if the category of the combo in the target node is equal to the category whose weight we are trying to change
            if categoriesOfCombos[comboIndex] == category:
                
                oldWeight = strategy[targetIndex][comboIndex]
                
                finalWeight = newWeight
                if addWeight:
                    finalWeight = oldWeight + newWeight
                    
                if finalWeight < 0:
                    raise Exception("Weight adjustment entered is invalid; cannot have negative percentage")
                
                if (printConsole):
                    print("oldWeight : " + str(oldWeight))
                    print("newWeight : " + str(finalWeight))
                    
                
                
                # iterate through all child nodes
                for childIndex in range(0,len(strategy)) :
                    if childIndex == targetIndex:
                        strategy[childIndex][comboIndex] = finalWeight
                    else :
                        # if the other decisions were 0, make them equally likely
                        if oldWeight == 1:
                            strategy[childIndex][comboIndex] = round((1 - finalWeight)/(len(strategy) - 1), 7)
                        #  if not, multiply a constant that will maintain their relative proportions
                        else:
                            k = (1 - newWeight)/(1 - oldWeight)
                            strategy[childIndex][comboIndex] = round(strategy[childIndex][comboIndex] * k, 7)
        return strategy


        
class Tests(unittest.TestCase):
    
    def __init__(self, methodName: solverPath = "runTest") -> None:
        super().__init__(methodName)
        self.sampleConnection = Solver(solverPath)
        self.samplePath = treePath(sampleCFR)
        self.sampleWeightsFile = currentdir + sampleFolder + "simple_weights.json"
    
        self.sampleConnection.command("load_tree " + self.samplePath)
        self.sampleConnection.command("load_all_nodes")

        self.nodelocker = TreeOperator(self.sampleConnection)
        
        self.comboWeights = fileReader.JSONtoMap(self.sampleWeightsFile)
        self.comboIndexes = fileReaderLocal.JSONtoMap(mappingsFolder + "handIndexMap")
        
    def testNodelocking(self):
        comboWeights = fileReader.JSONtoMap(self.sampleWeightsFile)
        comboIndexes = fileReaderLocal.JSONtoMap(mappingsFolder + "handIndexMap")
        
        self.assertEqual(list(comboWeights.keys()), ["ace_high"])
        
        nodeInfo = self.nodelocker.get_parent_and_id_of_targetNode(sampleNodeID)
        parentID = nodeInfo[0]
        targetIndex = nodeInfo[1]
        
        self.assertEqual(parentID, "r:0:c")
        
        oldStrategy = self.nodelocker.getCurrentStrategyAsList(parentID)
        
        for s in oldStrategy:
            self.assertEqual(len(s), totalCombos)
            self.assertEqual(s[0], 0.5)
        
        self.nodelocker.set_strategy([self.sampleWeightsFile, sampleNodeID])
        
        finalStrategy = self.nodelocker.getCurrentStrategyAsList(parentID)
        
        king_high_index = comboIndexes.get("AsQs")
        bd_2_index = comboIndexes.get("AhKh")
        
        ace_high_correct_weight = self.nodelocker.normalizeWeight(comboWeights.get("ace_high"))

        
        #printList(finalStrategy)
        
        self.assertAlmostEqual(finalStrategy[targetIndex][king_high_index], ace_high_correct_weight)
        self.assertAlmostEqual(finalStrategy[1-targetIndex][king_high_index], 1 - ace_high_correct_weight)
        self.assertAlmostEqual(finalStrategy[targetIndex][bd_2_index], bd_2_correct_weight)
        self.assertAlmostEqual(finalStrategy[1-targetIndex][bd_2_index], 1 - bd_2_correct_weight)
        

if __name__ == '__main__': 
    unittest.main()