from SolverConnection.solver import Solver
from logging_tools import parseStringToList
from outputs import fileWriter
from global_var import solverPath

connection = Solver(solverPath)
totalCombos = 1326
fpath = "C:\\" + "Users\degeneracy station\Documents\PioSolver-plugin\\"

def main() :
    cfrFile = "As5h3s"
    treePath = "\"C:\\" + "Users\\" + "degeneracy station\\" + "Documents\\" + "PioSolver-plugin\\" + cfrFile + ".cfr\""
    
    nodeID = "r:0:c"
    
    connection.command("load_tree " + treePath)
    connection.command("load_all_nodes")
    print("ready")
    # example output: ['r:0:c', 'IP_DEC', 'As 5h 3s', '0 0 55', '2 children', 'flags: PIO_CFR', '']
    op : list[str] = connection.command("show_node " + nodeID)
    # remove whitespace from board
    board : str = op[2].replace(" ", "")
    print(board)
    op = connection.command("show_category_names")
    hand_categories = parseStringToList(op[0])
    draw_categories = parseStringToList(op[1])
    
    hand_categ_map = {}
    draw_categ_map = {}
    
    i = 0
    for category in hand_categories:
        hand_categ_map[i] = category
        i = i + 1
    i = 0
    for category in draw_categories:
        draw_categ_map[i] = category
        i = i + 1
    
    fileWriter.mapToJSON("hand_categories.json", hand_categ_map)
    

if __name__ == "__main__":
    main()

