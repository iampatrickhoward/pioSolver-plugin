
from SolverConnection.solver import Solver
from logging_tools import parseOutputToList, makeString
from outputs import fileWriter
from global_var import solverPath


connection = Solver(solverPath)
totalCombos = 1326
handMap : dict[int, str] = {} 
    
def main ():
    # "C:\Users\degeneracy station\Documents\PioSolver-plugin\fullrange.cfr"
    
    # three trees with totally distinct flop boards and full ranges (so no dead combos)
    # any combo with card that is on board is considered outside range. Having three trees ensures every combo is hit at least once.
    fillHands("As5h3s")
    fillHands("KdTc9h")
    fillHands("Qh6c5s")
    
    for i in range(0,totalCombos):
        if i not in handMap:
            print(i)
    
    fileWriter.mapToJSON("handIndexMap.json", handMap)
    fileWriter.mapToCSV("handIndexMap.csv", handMap)

        

# shortcut to feed command line argument to PioSolver
def tellPio(string):
    op = (connection.command(string))
    return op

# sets 1326 strategies, each activating only index at a time, and checks the "readable" output from PioSolver to see which hand each index corresponds to
# then writes that hand to a map.
def fillHands(cfrFile: str):
    map : dict[int, str] = {} 
    treePath = "\"C:\\" + "Users\\" + "degeneracy station\\" + "Documents\\" + "PioSolver-plugin\\" + cfrFile + ".cfr\""
    print ("Filling hands using: " + cfrFile)
    
    nodeID = "r:0:c"
    
    tellPio("load_tree " + treePath)
    tellPio("load_all_nodes")

    for i in range(0,1326):
        tellPio("unlock_node " + nodeID)
        tellPio("set_strategy " + nodeID + " " + makeString(testStrategy(i)))
        tellPio("lock_node " + nodeID) 
        
        pioOutput = tellPio("show_strategy_pp " + nodeID)
        # a list of every single hand and the weight of both child nodes
        activeHandName = None
        # for each hand
        for hand in pioOutput:
            activeHandName = getHandNameIfActive(hand)
            # if this is the active hand, add it to the mapping and end loop
            if activeHandName is not None:
                handMap[i] = activeHandName
                break
            map[i] = activeHandName
    
    #write hand mapping to a .csv file
    # fileWriter.mapToCSV(fpath + cfrFile + ".csv", map)
    
    return map


# this takes the output of "show_strategy_pp", parses it into list [name of the hand,  % decision 1, % decision 2]
# then returns the name of the hand where the weight of decision one is not zero
def getHandNameIfActive(strInput : str) -> str:
    # delimit input using whitespace
    input : list[str] = parseOutputToList(strInput)
    # convert weights into floats
    if len(input) == 3:  
            input[1] = float(input[1])
            input[2] = float(input[2])
    
        # if weight of first decision is 0, return none, else return name of hand 
            #print(input)
            if input[1] == 0:
                return None
            else:
                return input[0]
    else: 
        return None
    

# generates a strategy for a 2-child node that makes one decision happen 100% the time with one hand and 0% with all the others
# we then run the "readable" strategy output (which has hand names) and parse to see which hand it is.
def testStrategy(x: int) -> list[float]:
    s = []
    for i in range(0,totalCombos):
        if (i == x):
            s.append(1)
        else:
            s.append(0)
    
    for i in range(0,totalCombos):
        if (i == x):
            s.append(0)
        else:
            s.append(1)
            
    return s


if __name__ == "__main__":
    main()

