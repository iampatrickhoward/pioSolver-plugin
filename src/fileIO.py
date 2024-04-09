import csv
import json
from global_var import currentdir
import unittest


class fileWriter():
    
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
        f = open(fpath + ".json")
        map : dict = json.load(f)
        f.close()
        return map
    
class fileReaderLocal(fileReader):
    
    @staticmethod
    def JSONtoMap(fname : str) -> dict:
        super(fileReaderLocal, fileReaderLocal).JSONtoMap(currentdir + fname)  
    
    @staticmethod
    def getLocalPath(fname : str) -> str:
        return currentdir + fname
    


class Tests(unittest.TestCase):

    def test_JSON_file_io(self):
        map = {"pop" : 1, "fizz" : 2, "cherry" : 3}
        fname = "testJSON"
        fileWriterLocal.mapToJSON(fname, map)
        
        output = fileReaderLocal.JSONtoMap(fname)
        for m in map:
            self.assertEqual(output.get(m), map.get(m))
    
    def test_mapToCSV(self):
        map = {"EV OOP" : 29, "EV IP" : 28}
        fname = "results.csv"
        fileWriterLocal.mapToCSV(fname, map)
        
            
if __name__ == '__main__': 
    unittest.main() 