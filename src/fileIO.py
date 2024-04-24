import csv
import json
from global_var import currentdir
import unittest 
from enum import Enum
from __future__ import annotations


class IO(Enum):
    APPEND = 1
    LOCAL = 2
    
class FileIO():
    
    @staticmethod
    def getSettings(fName : str, options = []) -> str:
        return ["a+" if (IO.APPEND in options) else "w+", currentdir + fName if (IO.LOCAL in options) else fName]
    
    @staticmethod
    def truncFile(fname: str) -> None:
        with open(fname, 'w', newline='') as file:
            #do nothing
            file.close()
            
class CSVio(FileIO):

    @staticmethod
    def addRow (fName: str, row: list, options = []) -> None:
        mode, path = CSVio.getSettings(fName, options)
        
        with open(path, mode, newline='') as file:
            w = csv.writer(file)
            w.writerow(row)
            file.close()
    
    @staticmethod
    def addRows (fName: str, grid: list[list], options = []) -> None:
        mode, path = CSVio.getSettings(fName, options)
        
        with open(path, mode, newline='') as file:
            w = csv.writer(file)
            w.writerows(grid)
            file.close()
    
class fileWriter():
    
    @staticmethod
    def truncFile(fname: str) -> None:
        with open(fname, 'w+', newline='') as file:
            #do nothing
            file.close()
    
    @staticmethod
    def gridToCSV(fName: str, grid: list[list]) -> None:
        with open(fName, 'a+', newline='') as file:
            w = csv.writer(file)
            for row in grid:
                w.writerow()
            file.close()
    
    @staticmethod
    def addRowToCSV(fName: str, row: list) -> None:
        with open(fName, 'a+', newline='') as file:
            w = csv.writer(file)
            w.writerow(row)
            file.close()
                   
    @staticmethod
    def mapToCSV(fname : str, map) -> None:        
        #print("writing to " + currentdir + fname + ".csv")
        with open(fname, 'w+', newline='') as file:
            w = csv.writer(file)
            for m in map:
                w.writerow([m, map[m]])
            file.close()
        
    @staticmethod
    def addMapToCSV(fname : str, map) -> None:        
        #print("writing to " + currentdir + fname + ".csv")
        with open(fname, 'a+', newline='') as file:
            w = csv.writer(file)
            for m in map:
                w.writerow([m, map[m]])
            file.close()

    @staticmethod
    def mapToJSON(fname : str, map):
        # print("writing to " + currentdir + fname + ".json")
        with open(fname + ".json", "w+") as file:
            json.dump(map, file)
            file.close()
        
class fileWriterLocal(fileWriter):
    
    @staticmethod
    def mapToCSV(fname : str, map) -> None:     
        super(fileWriterLocal, fileWriterLocal).mapToCSV(currentdir + fname, map)   
        
    @staticmethod
    def addMapToCSV(fname : str, map) -> None:        
        super(fileWriterLocal, fileWriterLocal).addMapToCSV(currentdir + fname, map)   

    @staticmethod
    def mapToJSON(fname : str, map):
        super(fileWriterLocal, fileWriterLocal).mapToJSON(currentdir + fname, map)     

class fileReader():
    @staticmethod
    def JSONtoMap(fpath : str) -> dict:
        # print("reading from " + currentdir + fname + ".json")
        f = open(fpath)
        map : dict = json.load(f)
        f.close()
        return map
    
class fileReaderLocal(fileReader):
    
    @staticmethod
    def JSONtoMap(fname : str) -> dict:
        super(fileReaderLocal, fileReaderLocal).JSONtoMap(currentdir + fname + ".json")  
    
    @staticmethod
    def getLocalPath(fname : str) -> str:
        return currentdir + fname
    


class Tests(unittest.TestCase):

    
    def test_mapToCSV(self):
        map = {"EV OOP" : 29, "EV IP" : 28}
        fname = "results.csv"
        fileWriterLocal.mapToCSV(fname, map)
        
    def testAddRowToCSV(self):
        CSVio.addRow("test.csv", ["EV", 234], [IO.LOCAL, IO.APPEND])
        
    def testTruncate(self):
        CSVio.truncFile("test.csv")
        CSVio.addRow("test.csv", ["Board", "EV OOP", "EV IP"], [IO.APPEND])
        
            
if __name__ == '__main__': 
    unittest.main() 