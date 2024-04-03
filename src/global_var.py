import os

solverPath = "C:\PioSOLVER\PioSOLVER3-pro.exe"
currentdir = os.getcwd() + "\\"
totalCombos = 1326
mappingsFolder = "mappings\\"

# for testing
# "C:\Users\degeneracy station\Documents\PioSolver-plugin\sample"
sampleFolder = "sample\\"
# "C:\Users\degeneracy station\Documents\PioSolver-plugin\sample\As5h3s.cfr"
sampleCFR = sampleFolder + "As5h3s"
# has 1 sister node
sampleNodeID = "r:0:c:c"

exception_categories = {"bdfd_1card": 1,
                        "bdfd_2card": 2}

hand_category_index = {"nothing": 0,
                       "king_high": 1,
                       "ace_high": 2,
                       "low_pair": 3,
                       "3rd-pair": 4,
                       "2nd-pair": 5,
                       "underpair": 6,
                       "top_pair": 7,
                       "top_pair_tp": 8,
                       "overpair": 9,
                       "two_pair": 10,
                       "trips": 11, 
                       "set": 12,
                       "straight": 13,
                       "flush": 14,
                       "fullhouse": 15,
                       "top_fullhouse": 16,
                       "quads": 17,
                       "straight_flush": 18}

draw_category_index = {"no_draw": 0,
                       "bdfd_1card": 1,
                       "bdfd_2card": 2,
                       "4out_straight_draw": 3,
                       "8out_straight_draw": 4,
                       "flush_draw": 5,
                       "combo_draw": 6}

'''
def main():
    # this specifies you're referring to the global variable, not a new variable within the scope of the function
    global hand_category_index
    global draw_category_index
    global exception_categories

    # format: {"nothing": 0, "king_high": 1, "ace_high": 2, "low_pair": 3...
    hand_category_index = fileReaderLocal.JSONtoMap(mappingsFolder + "hand_categories")
    # format: {"no_draw": 0, "bdfd_1card": 1, "bdfd_2card": 2, ...
    draw_category_index = fileReaderLocal.JSONtoMap(mappingsFolder + "draw_categories")
    # there are certain draw categories where the weight inputted by the user is meant to be added to the original weight rather than replacing it
    exception_categories = fileReaderLocal.JSONtoMap(mappingsFolder + "exception_categories")
        

show_children r:0:c


child 0:

r:0:c:b16
OOP_DEC
As 5h 3s
0 16 55
3 children
flags: PIO_CFR

child 1:

r:0:c:c
SPLIT_NODE
As 5h 3s
0 0 55
49 children
flags:



if __name__ == '__main__': 
    main() 

'''