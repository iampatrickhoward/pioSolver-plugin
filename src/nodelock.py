from SolverConnection.solver import Solver
from logging_tools import parseStringToList, printList, treePath, makeString
from fileIO import fileWriter, fileReader
from global_var import solverPath, totalCombos
import unittest

connection = Solver(solverPath)

def main() :
    
    #makeMappings()

    folder = "cfrFiles\\"
    cfrFile = folder +  "As5h3s"
    path = treePath(cfrFile)
    
    nodeID = "r:0:c"
    
    connection.command("load_tree " + path)
    connection.command("load_all_nodes")
    
    weightMap = fileReader.JSONtoMap(folder + "weights")
    
    
    # choose a child whose strategy to alter
    whichChild = 1
    
    # get the IDs of all the node's children
    childIDs = getChildIDs(nodeID)
    child = childIDs[whichChild]
    
    all_strats = connection.command("show_strategy " + nodeID)
    print(all_strats)
    # take strategy of child node, turn numbers in string to numbers in list
    strategy = parseStringToList(all_strats[whichChild])
    
    # derives the hand and draw categories of hands in child node from pio output
    categories = parseCategories(child)
    hand_cats = categories[0]
    draw_cats = categories[1]
    
    
    
    all_strats[whichChild] = makeString(strategy)
    newNodeStrategy  = makeString(all_strats)
    
    command = "set_strategy " + nodeID + " " + newNodeStrategy
    
    connection.command(command)
    
    checkStrat = connection.command("show_strategy " + nodeID)
    print("----------------------------------------------")
    print(checkStrat)
    
    



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
    return board

    
def parseCategories(nodeID):
    op = connection.command("show_categories " + getBoard(nodeID))
    # a 1326 length list of integers, each referencing the hand category the corresponding combo belongs to.
    hand_per_combo = parseStringToList(op[0])
    draw_per_combo = parseStringToList(op[1])
    return [hand_per_combo, draw_per_combo]

# checks if category is draw or hand category and updates weights accordingly
def alter_strategy(strategy : list[float], weightMap : dict[str, int], child: int) -> list[float]:
    hand_category_index = fileReader.JSONtoMap("hand_categories")
    draw_category_index = fileReader.JSONtoMap("draw_categories")
    
    # derives the hand and draw categories of hands in child node from pio output
    categories = parseCategories(child)
    hand_cats = categories[0]
    draw_cats = categories[1]
    
    for category_name in weightMap:
        if category_name in hand_category_index:
            strategy = update_weight(strategy, hand_cats, hand_category_index.get(category_name), weightMap.get(category_name))
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


if __name__ == "__main__":
    main()

