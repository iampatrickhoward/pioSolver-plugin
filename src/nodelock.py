from SolverConnection.solver import Solver
from logging_tools import parseStringToList, printList, treePath, makeString
from fileIO import fileWriter, fileReader
from global_var import solverPath, totalCombos
import unittest

connection = Solver(solverPath)
folder = "cfrFiles\\"
cfrFile = folder +  "As5h3s"
path = treePath(cfrFile)
    
nodeID = "r:0:c"
    
connection.command("load_tree " + path)
connection.command("load_all_nodes")

def run() :
    
    #makeMappings()
    
    weightMap = fileReader.JSONtoMap(folder + "weights")
    
    
    # choose a child whose strategy to alter
    whichChild = 1
    # get the IDs of all the node's children
    childIDs = getChildIDs(nodeID)
    targetID = childIDs[whichChild]
    
    strategy_output = connection.command("show_strategy " + nodeID) 
    
    printList(strategy_output)
    
    # take the strategy of the child and turn it into a list of numbers
    targetStrategy = parseStringToList(strategy_output[whichChild])
    
    alter_strategy(targetStrategy, weightMap, targetID)
    
    # set the new target strategy in the original pio output 
    strategy_output[whichChild] = makeString(targetStrategy)
    
    # pio outputs strategy as list but reads it as string, so must convert whole thing to string again
    newStrategy  = makeString(strategy_output)
    
    command = "set_strategy " + nodeID + " " + newStrategy
    
    connection.command(command)
    
    checkStrat = connection.command("show_strategy " + nodeID)
    
    print(f"\n \n------------------------------------------------------------------------------ \n \n")
    printList(checkStrat)
    
    



def getChildIDs (nodeID : str) -> list[str] :
    # example output: 
    # ['child 0:', 'r:0:c:b16', 'OOP_DEC', 'As 5h 3s', '0 16 55', '3 children', 'flags: PIO_CFR', '', 'child 1:', 'r:0:c:c', 'SPLIT_NODE', 'As 5h 3s', '0 0 55', '49 children', 'flags:', '']
    output = connection.command("show_children " + nodeID) 
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
def getBoard(nodeID : str) -> str:
    # example output: ['r:0:c', 'IP_DEC', 'As 5h 3s', '0 0 55', '2 children', 'flags: PIO_CFR', '']
    op : list[str] = connection.command("show_node " + nodeID)
    # remove whitespace from board
    board : str = op[2].replace(" ", "")
    # format As5h3s
    return board

    
def parseCategories(nodeID):
    op = connection.command("show_categories " + getBoard(nodeID))
    # a 1326 length list of integers, each referencing the hand category the corresponding combo belongs to.
    hand_per_combo = parseStringToList(op[0])
    draw_per_combo = parseStringToList(op[1])
    return [hand_per_combo, draw_per_combo]

# checks if category is draw or hand category and updates weights accordingly
def alter_strategy(strategy : list[float], weightMap : dict[str, int], nodeID: str) -> list[float]:
    # format: {"nothing": 0, "king_high": 1, "ace_high": 2, "low_pair": 3...
    
    hand_category_index = fileReader.JSONtoMap("mappings\\" + "hand_categories")
    # format: {"no_draw": 0, "bdfd_1card": 1, "bdfd_2card": 2, ...
    draw_category_index = fileReader.JSONtoMap("mappings\\" + "draw_categories")
    
    # derives the hand and draw categories of hands in child node from pio output
    categories = parseCategories(nodeID)
    hand_cats = categories[0]
    draw_cats = categories[1]
    
    for category_name in weightMap:
        # if it is a hand category
        if category_name in hand_category_index:
            # inputs: the current strategy, the index corresponding to the category name, the weight of that category)
            strategy = update_weight(strategy, hand_cats, hand_category_index.get(category_name), weightMap.get(category_name))
        # if it is a draw category
        if category_name in draw_category_index:
            strategy = update_weight(strategy, draw_cats, draw_category_index.get(category_name), weightMap.get(category_name))

#alters the hands that belong to the given category to the given weight
def update_weight(strategy : list[float], categoryOfCombo : list[int], targetCategory : int, weight : float) -> list[float]:
    for i in range(0,totalCombos):
        if categoryOfCombo[i] == targetCategory:
            # when entering in weights, could be decimal or percentage. account for inconsistency in human entry (20% could be typed in as .2 or 20)
            if (weight > 1):
                weight = weight/100
            strategy[i] = weight
    return strategy


def getChildNodeStrategy(nodeID: str, whichChild: int):
        all_strats = connection.command("show_strategy " + nodeID)
        # take strategy of child node, turn numbers in string to numbers in list
        return  parseStringToList(all_strats[whichChild])
        
class Tests(unittest.TestCase):

    def testReadWeightMap(self):
        print (fileReader.JSONtoMap(folder + "weights"))
        
    def testGetStrategy(self):
        print(getChildNodeStrategy(nodeID, 1))
        
    def testParseCategories(self):
        printList(parseCategories(nodeID))
        

if __name__ == '__main__': 
    run()