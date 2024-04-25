from __future__ import annotations
import csv
import json
from global_var import currentdir
import unittest 
from enum import Enum


class IO(Enum):
    APPEND = 1
    LOCAL = 2


def getIOSettings(fName : str, options = []) -> str:
    return ["a+" if (IO.APPEND in options) else "w+", currentdir + fName if (IO.LOCAL in options) else fName]

def addRowtoCSV (fName: str, row: list, options = []) -> None:
    mode, path = getIOSettings(fName, options)
    path = checkPath(path, ".csv")
    
    with open(path, mode, newline='') as file:
        w = csv.writer(file)
        w.writerow(row)
        file.close()

def JSONtoMap(fName : str, options = []) -> dict:
    mode, path = CSVio.getIOSettings(fName, options)
    path = checkPath(path, ".json")
    
    with open(path, mode, newline='') as file:
        map : dict = json.load(file)
        file.close()
        return map

def checkPath (path, correctExtension):
    if getExtension(path) == correctExtension:
        return path
    elif getExtension(path) == None: 
        return path + correctExtension
    else:
        raise Exception("File passed does not have correct extension.")
    
def getExtension(file:str) -> str:
    i = file.split(".")[1]
    if len(i) < 2:
        return None
    else:
        return i[1]
    
class Tests(unittest.TestCase):
            
    def testAddRowToCSV(self):
        addRowtoCSV("test.csv", ["EV", 234], [IO.LOCAL, IO.APPEND])

        
            
if __name__ == '__main__': 
    unittest.main() 