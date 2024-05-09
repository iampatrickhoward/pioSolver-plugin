from __future__ import annotations
from stringFunc import parseStringToList, parseNodeIDtoList, makeNodeIDfromList, parseStrategyToList, makeStrategyFromList, makeString
from global_var import totalCombos, hand_category_index, draw_category_index, exception_categories
from decimal import Decimal, getcontext
from global_var import solverPath, currentdir, accuracy
from SolverConnection.solver import Solver
import unittest
from inputs import WeightsFile


printConsole = True


def tryPio(connection, func , args : list): 
        try:
            #command not meant to have any inputs
            if args is None or len(args) == 0:
                return func()
            #command meant to take a single input
            elif len(args) == 1:
                return func(args[0])
            #command meant to take a list of inputs
            else:
                return func(args)
        except Exception as e:
            connection.exit()
            raise e

# when entering in weights in JSON, could be decimal or percentage. 
# this accounts for inconsistency in human entry (20% could be typed in as .2 or 20)   
def normalizeWeight(n: float) -> float:
    if (n > 1):
        n = Decimal(n)/Decimal(100)
    return n
    
class nodeFamily():
    def __init__(self, nodeID : str, parent : str = "", index : int = 0, sisters : list[str] = [], children : list[str] = []) -> None:
        self.nodeID = nodeID
        self.parent = parent
        self.index = index
        self.sisters = sisters
        self.children = children

class nodeInfo():
    def __init__(self, nodeID : str, type : str = "", board : str = "", pot : str = "") -> None:
        self.nodeID = nodeID
        self.type = type
        self.board = board
        self.pot = pot
        
class TreeOperator(): 
    def __init__(self, connection):
        self.connection = connection
        if tryPio(self.connection, self.connection.command, ["is_tree_present"]) == "false":
            raise Exception("No tree is loaded; cannot perform tree operations")
        
        getcontext().prec = 9
    
    # args[0] nodeId
    # args[1] weightsFile
    def set_strategy(self, args : list) :
        nodeID = args[0]
        family = self.get_family(nodeID)
        weightMap = args[1]
        
        self.connection.command("unlock_node " + family.parent) 
        
        # the strategy map of the target node and all its sister nodeq
        # format: a list of a list of 1326 floats (one per combo)
        strategy = self.getCurrentStrategyAsList(family.parent)
        
        self.alter_strategy(strategy, weightMap, family.index, nodeID)
        
        # set the new target strategy in the original pio output 
        strategy = makeStrategyFromList(strategy)
        
        self.connection.command("set_strategy " + family.parent + " " + strategy)
                
        if printConsole:
            print("--------------------------------------------------------")
            print(strategy)
        
        self.connection.command("lock_node " + family.parent) 
    
    def getCurrentStrategyAsList(self, nodeID: str) -> list[list[float]] :
        strategy = self.connection.command("show_strategy " + nodeID)
        # turn each individual strategy (string) in the list into a list of numbers
        return parseStrategyToList(strategy) 

    # in order to nodelock a particular decision, we need to reference it by its index number as the child of the parent
    # this takes a node and returns both in the form [parentNodeID, [sister node IDs], index]
    def get_family(self, nodeID : str) -> nodeFamily:
        family = nodeFamily(nodeID=nodeID)
        
        family.children = self.getChildIDs(nodeID)
        nodes = parseNodeIDtoList(nodeID)
        # remove last decision to get parents
        nodes.pop()
        # turn list back into ID
        family.parent = makeNodeIDfromList(nodes)
        family.sisters = self.getChildIDs(family.parent)
        index = 0
        for id in family.sisters:
            if id == nodeID:
                family.index = index
                return family
            index = index + 1
            
        error = "Invalid decision node - the child nodes of " + family.parent + " are: "
        for id in family.sisters:
            error = error + " " + id
        raise Exception(error)
        

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
    
    # gets the info at the current node 
    def getNodeInfo(self, nodeID : str) -> str:
        # example output: ['r:0:c', 'IP_DEC', 'As 5h 3s', '0 0 55', '2 children', 'flags: PIO_CFR', '']
        op : list[str] = self.connection.command("show_node " + nodeID)
        info = nodeInfo(nodeID=nodeID)
        info.type = op[1]
        # gets the board at the current node in a format that can be fed to other commands (remove whitspace to get format like As5h3s)
        info.board = op[2].replace(" ", "")
        info.pot = op[3]
        return info

    # gets range at particular node
    def getRange(self, nodeID : str) -> str:
        oop_range : str = makeString(self.connection.command("show_range OOP " + nodeID))
        ip_range : str = makeString(self.connection.command("show_range IP " + nodeID))
        return [oop_range, ip_range]
       
    def parseCategories(self, nodeID):
        op = self.connection.command("show_categories " + self.getNodeInfo(nodeID).board)
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
    
    # alters the combos that belong to the given category to the given weight
    # updates the corresponding combos in the other child nodes to a weight that keeps the proportions of the other strategies the same as before
    def update_weight(self, strategy : list[list[float]], targetIndex : int, categoriesOfCombos : list[int], category : int, newWeight : float, addWeight : bool) -> list[float]:
        newWeight = Decimal(normalizeWeight(newWeight))
        
        for comboIndex in range(0,totalCombos):
            # if the category of the combo in the target node is equal to the category whose weight we are trying to change
            if categoriesOfCombos[comboIndex] == category:
                
                oldWeight = Decimal(strategy[targetIndex][comboIndex])
                
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
                            strategy[childIndex][comboIndex] = (Decimal(1) - finalWeight)/(Decimal(len(strategy) - 1))
                        #  if not, multiply a constant that will maintain their relative proportions
                        else:
                            k = (Decimal(1) - newWeight)/(Decimal(1) - oldWeight)
                            strategy[childIndex][comboIndex] = Decimal(strategy[childIndex][comboIndex])* Decimal(k)
        return strategy


class Tests(unittest.TestCase):
    
    def testQc8cTsResults(self):
        folder = currentdir + "\sample"
        cfr = folder + r"\Qc8cTs\og.cfr"
        node = "r:0:c:b16"
        
        weights = WeightsFile("test").parseInput(folder + r"\buggy_weights.json")
        
        connection = Solver(solverPath)
        connection.write_line("load_tree \"" + cfr)
        connection.wait_line("load_tree ok!")
        
        connection.write_line("load_all_nodes")
        connection.wait_line("load_all_nodes ok!")
        
        connection.read_until_end()
        
        #t = TreeOperator(connection)
        #index = t.get_family(node).index
        #t.set_strategy([node, weights])
        
        strategy = connection.command("show_strategy " + node)
        
        for s in strategy:
            print(s)
        #self.assertEqual(strategy[index], "0.500001729 0.50000304 0.49999994 0.50000006 0.500000119 0.50000006 0 0 0 0 0 0 0 0 0.499999464 0 0 0 0 0.5 0.50000006 0 0 0 0 0.500000298 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.49999997 0 0 0 0 0 0 0 0 0.50000006 0.5 0 0 0 0 0 0 0 0 0.500000179 0.50000006 0.50000006 0 0 0 0 0.75 0 0 0 0.750000298 0 0 0 0 0 0 0 0 0.50000006 0 0 0 0.5 0 0 0.50000006 0 0 0 0 0 0 0.50000006 0 0 0 0.50000006 0 0.5 0.5 0 0 0 0 0 0 0 0.499999464 0 0 0 1 0.49999994 0.5 0.5 0 0 0 0 0 0 0 0 0.75 0 0 0 0.750000119 0 0 0 0 0 0 0 0 0 0 0 0 0.50000006 0 0 0 0.5 0 0 0.5 0 0 0 0 0 0 0 0 0 0 0.499998212 0 0 0 1 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0.5 0.50000006 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0.75 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.75000006 0 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.75000006 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.74999994 0.5 0.5 0.50000006 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.50000006 0 0 0 0.50000006 0 0 0 0.50000006 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.500000119 0 0 0 0.50000006 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.49999997 0 0 0 0.5 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0 0.500000119 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.75000006 0 0 0 0.75000006 0 0 0 0.5 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.74999994 0 0 0 0.75 0 0 0.5 0.5 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.75 0 0 0 0.75000006 0 0.5 0.5 0.5 0.5 0.500000119 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.500000238 0 0 0 0.500000119 0 0 0 0 1 1 1 0.5 0.5 0.49999994 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.500000775 0 0 0 0.500001252 0 0 0 1 1 1 0.500000119 0.499999881 0.5 0.5 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.500001311 0 0 0 0.499999195 0 0 1 1 1 0.500000119 0.499999881 0.5 0.500000238 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 1 0 0 0 0 0.5 0.5 0.5 1 1 1 1 0.5 0.5 0.499999881 0 0 0 0 0 0 0 0 0 0 0.75 0 0 0 0.75 0 0 0 0.75 0 0 0 0.75 0 0 0 0.5 0.5 0.5 1 1 1 1 0.5 0.5 0.5 0 0.250000209 0 0 0 0 0 0 0 0 0 0 0.74999994 0 0 0 0.750000119 0 0 0 0.75 0 0 0 0.75 0 0 0.5 0.5 0.5 1 1 1 1 0.5 0.5 0.5 0 0.250000209 0.249999911 0 0 0 0 0 0 0 0 0 0 0 0.749999881 0 0 0 0.75000006 0 0 0 0.75 0 0 0 0.75 0 0.5 0.5 0.5 1 1 1 1 0.5 0.5 0.5 0 0.25 0.249999911 0.250000298 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.50000006 0 0 0 0.500000238 0 0 0 0.500000119 0 0 0 0.500000119 0 0 0 0.5 0 0 0 0.5 0 0 0 1 0 0 0.499999821 0.5 0.500000119 0.49999994 1 1 1 0 0.500000179 0.5 0.500000179 0.5 0 0 0 0.500000238 0 0 0 0.50000006 0 0 0 0.500000119 0 0 0 0.50000006 0 0 0 0.5 0 0 0 0.5 0 0 0 1 0 0.5 0.500000119 0.5 0.500000119 1 1 1 0 0.499999702 0.5 0.5 0.500000119 0 1 0 0 0 0.500000119 0 0 0 0.500000119 0 0 0 0.50000006 0 0 0 0.500000358 0 0 0 0.500000358 0 0 0 0.5 0 0 0 1 0.500000119 0.5 0.5 0.5 1 1 1 0 0.500000119 0.5 0.499999911 0.5 0 1 1 0.750000179 0 0 0 0.74999994 0 0 0 0.75 0 0 0 0.75 0 0 0 0.750000179 0 0 0 0.75 0 0 0 0 0.5 0.5 0.5 1 0.750000238 0.750000119 0.75 0.5 0.50000006 0.50000006 0 1 0.75 0.75000006 0.75 0 0.500000119 0.50000006 0.50000006 0 0.49999997 0 0 0 0.50000006 0 0 0 0.499999881 0 0 0 0.49999997 0 0 0 0.50000006 0 0 0 0.499999911 0 0 0 0.50000006 0.50000006 0.5 0.75000006 0.750000119 0.750000119 0.75 0.49999994 0.5 0.5 0 0.74999994 0.75000006 0.75 0.75 0 0.5 0.49999994 0.5 1 0 0 0.50000006 0 0 0 0.500000417 0 0 0 0.49999997 0 0 0 0.5 0 0 0 0.5 0 0 0 0.5 0 0 0.50000006 0.5 0.5 0.749999881 0.750000119 0.75000006 0.75 0.5 0.5 0.5 0 0.74999994 0.75 0.750000119 0.74999994 0 0.5 0.50000006 0.5 1 1 0 0 0 0.49999994 0 0 0 0.50000006 0 0 0 0.50000006 0 0 0 0.49999994 0 0 0 0.5 0 0 0 0.5 0 0.5 0.5 0.5 0.75000006 0.75000006 0.75 0.75 0.5 0.499999911 0.500000119 0 0.750000119 0.75 0.75 1 0 0.50000006 0.5 0.5 1 1 1 0.749999881 0 0 0 0.750000298 0 0 0 0.750000298 0.500000477 0.500000417 0.49999997 0.75 0.500000179 0.50000006 0.49999997 0.74999994 0.50000006 0.5 0.50000006 0.750000238 0.50000006 0.49999997 0.500000238 0 0.49999994 0.500000119 0.5 1 0.75000006 0.75 0.749999881 0.5 0.50000006 0.50000006 0 1 0.75 0.75 0.75000006 0 0.50000006 0.499999911 0.5 1 0.750000119 0.75 0.750000358 0 0.500000477 0 0 0 0.49999994 0 0 0.5 0.49999994 0.50000006 0.5 1 0.5 0.5 0.5 0.50000006 0.5 0.50000006 0.50000006 0.5 0.5 0.5 0.5 0 0.5 0.5 0.5 0.750000119 0.75 0.750000119 1 0.49999994 0.50000006 0.50000006 0 0.75 0.75000006 0.74999994 0.75 0 0.50000006 0.49999994 0.5 0.75 0.750000119 0.75 0.750000119 1 0 0 0.500001192 0 0 0 0.499999851 0 1 0.5 0.50000006 0.50000006 1 0.5 0.5 0.50000006 0.50000006 0.5 0.5 0.49999994 0.500000119 0.5 0.5 0.50000006 0 0.5 0.5 0.5 0.75 0.75000006 0.75000006 0.75 0.5 0.5 0.50000006 0 0.75 0.75 0.74999994 0.75 0 0.50000006 0.49999994 0.5 0.75 0.75000006 0.75000006 0.75 1 1 0 0 0 0.50000006 0 0 0 0.5 1 0.5 0.50000006 0.50000006 1 0.50000006 0.50000006 0.5 0.50000006 0.5 0.50000006 0.49999994 0.49999994 0.5 0.49999994 0.5 0 0.50000006 0.5 1 0.75 0.75000006 0.75 0.75 0.5 0.50000006 0.5 0 0.74999994 0.75 0.75 1 0 0.49999994 0.49999994 0.5 0.750000119 0.75 0.750000119 0.75 1 1 1")
        #self.assertEqual(strategy[index-1], "0.499998242 0.49999696 0.50000006 0.499999911 0.499999881 0.49999997 0 0 0 0 0 0 0 0 0.500000536 0 0 0 0 0.5 0.49999994 0 0 0 0 0.499999672 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.50000006 0 0 0 0 0 0 0 0 0.49999997 0.5 0 0 0 0 0 0 0 0 0.499999851 0.49999994 0.49999994 0 0 0 0 0.25 0 0 0 0.249999702 0 0 0 0 0 0 0 0 0.49999994 0 0 0 0.5 0 0 0.49999997 0 0 0 0 0 0 0.49999994 0 0 0 0.49999994 0 0.5 0.5 0 0 0 0 0 0 0 0.500000536 0 0 0 0 0.50000006 0.5 0.5 0 0 0 0 0 0 0 0 0.25 0 0 0 0.249999866 0 0 0 0 0 0 0 0 0 0 0 0 0.49999997 0 0 0 0.5 0 0 0.5 0 0 0 0 0 0 0 0 0 0 0.500001788 0 0 0 0 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.49999994 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.24999994 0 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.24999994 0 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.25000006 0.5 0.5 0.49999994 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.49999997 0 0 0 0.49999994 0 0 0 0.49999997 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.499999851 0 0 0 0.49999997 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0 0 0 0.50000006 0 0 0 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.499999881 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.249999925 0 0 0 0.249999955 0 0 0 0.5 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25000006 0 0 0 0.25 0 0 0.5 0.5 0.5 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0 0 0 0.249999925 0 0.5 0.5 0.5 0.5 0.499999911 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.499999791 0 0 0 0.499999881 0 0 0 0 0 0 0 0.5 0.5 0.50000006 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.499999255 0 0 0 0.499998719 0 0 0 0 0 0 0.499999881 0.500000119 0.5 0.5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.499998689 0 0 0 0.500000834 0 0 0 0 0 0.499999881 0.500000119 0.5 0.499999762 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.5 0.5 0.5 0 0 0 0 0.5 0.5 0.500000119 0 0 0 0 0 0 0 0 0 0 0.25 0 0 0 0.25 0 0 0 0.25 0 0 0 0.25 0 0 0 0.5 0.5 0.5 0 0 0 0 0.5 0.5 0.5 0 0.749999762 0 0 0 0 0 0 0 0 0 0 0.25000006 0 0 0 0.249999881 0 0 0 0.25 0 0 0 0.25 0 0 0.5 0.5 0.5 0 0 0 0 0.5 0.5 0.5 0 0.749999762 0.75000006 0 0 0 0 0 0 0 0 0 0 0 0.250000119 0 0 0 0.24999994 0 0 0 0.25 0 0 0 0.25 0 0.5 0.5 0.5 0 0 0 0 0.5 0.5 0.5 0 0.75 0.75000006 0.749999702 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.49999994 0 0 0 0.499999732 0 0 0 0.499999881 0 0 0 0.499999881 0 0 0 0.5 0 0 0 0.5 0 0 0 0 0 0 0.500000179 0.5 0.499999851 0.500000119 0 0 0 0 0.499999821 0.5 0.499999821 0.5 0 0 0 0.499999732 0 0 0 0.49999994 0 0 0 0.499999881 0 0 0 0.49999994 0 0 0 0.5 0 0 0 0.5 0 0 0 0 0 0.5 0.499999851 0.5 0.499999911 0 0 0 0 0.500000298 0.5 0.5 0.499999881 0 0 0 0 0 0.499999911 0 0 0 0.499999911 0 0 0 0.49999994 0 0 0 0.499999642 0 0 0 0.499999642 0 0 0 0.5 0 0 0 0 0.499999851 0.5 0.5 0.5 0 0 0 0 0.499999881 0.5 0.50000006 0.5 0 0 0 0.249999821 0 0 0 0.25000006 0 0 0 0.25 0 0 0 0.25 0 0 0 0.249999821 0 0 0 0.25 0 0 0 0 0.5 0.5 0.5 0 0.249999762 0.249999881 0.25 0.5 0.49999994 0.49999994 0 0 0.25 0.24999994 0.25 0 0.499999911 0.49999994 0.49999994 0 0.50000006 0 0 0 0.499999911 0 0 0 0.500000119 0 0 0 0.50000006 0 0 0 0.49999994 0 0 0 0.50000006 0 0 0 0.49999994 0.49999994 0.5 0.24999994 0.249999881 0.249999881 0.25 0.50000006 0.5 0.5 0 0.25000006 0.24999994 0.25 0.25 0 0.5 0.50000006 0.5 0 0 0 0.499999911 0 0 0 0.499999553 0 0 0 0.50000006 0 0 0 0.5 0 0 0 0.5 0 0 0 0.5 0 0 0.49999994 0.5 0.5 0.250000119 0.249999881 0.24999994 0.25 0.5 0.5 0.5 0 0.25000006 0.25 0.249999896 0.25000006 0 0.5 0.49999997 0.5 0 0 0 0 0 0.50000006 0 0 0 0.49999997 0 0 0 0.49999997 0 0 0 0.50000006 0 0 0 0.5 0 0 0 0.5 0 0.5 0.5 0.5 0.24999994 0.24999994 0.25 0.25 0.5 0.50000006 0.499999881 0 0.249999881 0.25 0.25 0 0 0.49999994 0.5 0.5 0 0 0 0.250000119 0 0 0 0.249999702 0 0 0 0.249999687 0.499999523 0.499999583 0.50000006 0.25 0.499999821 0.49999997 0.50000006 0.25000006 0.49999997 0.5 0.49999997 0.249999762 0.49999997 0.50000006 0.499999762 0 0.50000006 0.499999881 0.5 0 0.24999994 0.25 0.250000119 0.5 0.49999994 0.49999994 0 0 0.25 0.25 0.249999925 0 0.49999994 0.50000006 0.5 0 0.249999881 0.25 0.249999642 0 0.499999523 0 0 0 0.50000006 0 0 0.5 0.50000006 0.49999997 0.5 0 0.5 0.5 0.5 0.49999997 0.5 0.49999994 0.49999997 0.5 0.5 0.5 0.5 0 0.5 0.5 0.5 0.249999881 0.25 0.249999881 0 0.50000006 0.49999994 0.49999994 0 0.25 0.24999994 0.25000006 0.25 0 0.49999997 0.50000006 0.5 0.25 0.249999881 0.25 0.249999896 0 0 0 0.499998808 0 0 0 0.500000119 0 0 0.5 0.49999997 0.49999997 0 0.5 0.5 0.49999994 0.49999997 0.5 0.5 0.50000006 0.499999881 0.5 0.5 0.49999994 0 0.5 0.5 0.5 0.25 0.24999994 0.24999994 0.25 0.5 0.5 0.49999994 0 0.25 0.25 0.25000006 0.25 0 0.49999997 0.50000006 0.5 0.25 0.249999955 0.249999955 0.25 0 0 0 0 0 0.49999997 0 0 0 0.5 0 0.5 0.49999997 0.49999994 0 0.49999997 0.49999997 0.5 0.49999997 0.5 0.49999994 0.50000006 0.50000006 0.5 0.50000006 0.5 0 0.49999994 0.5 0 0.25 0.24999994 0.25 0.25 0.5 0.49999994 0.5 0 0.25000006 0.25 0.25 0 0 0.50000006 0.50000006 0.5 0.249999881 0.25 0.249999881 0.25 0 0 0")
        
        
        
        connection.exit()
        
if __name__ == '__main__': 
    unittest.main() 

