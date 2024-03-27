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

'''
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
'''