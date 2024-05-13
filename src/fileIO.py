from __future__ import annotations
import csv
import json
from global_var import currentdir
import unittest 
from errorMessages import Errors
from enum import Enum


class IO(Enum):
    APPEND = 1
    LOCAL = 2


def getIOSettings(fName : str, options = []) -> str:
    return ["a+" if (IO.APPEND in options) else "w+", currentdir + fName if (IO.LOCAL in options) else fName]


def addRowstoCSV (fName: str, rows: list[list], options = []) -> None:
    mode, path = getIOSettings(fName, options)
    path = checkPath(path, ".csv")
    
    with open(path, mode, newline='') as file:
        w = csv.writer(file)
        for r in rows:
            w.writerow(r)
        file.close()

def addRowtoCSV (fName: str, row: list, options = []) -> None:
    mode, path = getIOSettings(fName, options)
    path = checkPath(path, ".csv")
    
    with open(path, mode, newline='') as file:
        w = csv.writer(file)
        w.writerow(row)
        file.close()


def JSONtoMap(fName : str, options = []) -> dict:
    mode = "r"
    path = currentdir + fName if (IO.LOCAL in options) else fName
    path = checkPath(path, ".json")
    
    with open(path, mode, newline='') as file:
        map : dict = json.load(file)
        file.close()
        return map

def mapToJSON(fName : str, map: dict, options = []) -> dict:
    mode, path = getIOSettings(fName, options)
    path = checkPath(path, ".json")
    
    with open(path, mode, newline='') as file:
        json.dump(map, file)
        file.close()
        return map

def checkPath (path, correctExtension):
    correctExtension = correctExtension.strip(".")
    if getExtension(path) == correctExtension:
        return path
    elif getExtension(path) is None: 
        return path + "." + correctExtension
    else:
        raise Exception(Errors.wrongFileType(correctExtension))
    
def getExtension(file:str) -> str:
    i = file.split(".")
    if len(i) < 2:
        return None
    else:
        return i[len(i) - 1]


hand_index_map = JSONtoMap("\mappings\handIndexMap.json", [IO.LOCAL])
hands = list(hand_index_map.keys())

class Tests(unittest.TestCase):
    
    def testGetExtension(self):
        self.assertEqual(getExtension("test.csv"), "csv")
        self.assertEqual(getExtension("test"), None)
        self.assertEqual(getExtension("C:\PioSOLVER\PioSOLVER3-pro.exe"), "exe")
        self.assertEqual(getExtension("C:\PioSOLVER.2.0\PioSOLVER3-pro.exe"), "exe")
        
    def testCheckPath(self):
        self.assertEqual(checkPath("test.csv", ".csv"), "test.csv")
        self.assertEqual(checkPath("test.csv", "csv"), "test.csv")
        self.assertEqual(checkPath("test", "csv"), "test.csv")
        try:
            checkPath("test.json", "csv")
        except Exception as e:
            self.assertEqual(str(e), Errors.wrongFileType("csv"))
            
    def testAddRowToCSV(self):
        addRowtoCSV("test.csv", ["EV", 234], [IO.LOCAL, IO.APPEND])
        addRowstoCSV("test.csv", [["RR", "rstrs"], ["EV", 560]], [IO.LOCAL, IO.APPEND])

        
            
if __name__ == '__main__': 
    unittest.main() 