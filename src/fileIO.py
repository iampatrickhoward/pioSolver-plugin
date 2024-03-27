import csv
import json
from global_var import currentdir
import unittest


class fileWriter():
    
    def mapToCSV(fname : str, map) -> None:        
        # print("writing to " + currentdir + fname + ".csv")
        with open(currentdir + fname, 'w+', newline='') as file:
            w = csv.writer(file)
            for m in map:
                w.writerow([m, map[m]])
        file.close()

    def mapToJSON(fname : str, map):
        # print("writing to " + currentdir + fname + ".json")
        with open(currentdir + fname + ".json", "w+") as file:
            json.dump(map, file)
        file.close()

class fileReader():
    def JSONtoMap(fname : str) -> dict:
        # print("reading from " + currentdir + fname + ".json")
        f = open(currentdir + fname + ".json")
        map = json.load(f)
        f.close()
        return map
    


class Tests(unittest.TestCase):

    def test_JSON_file_io(self):
        map = {"pop" : 1, "fizz" : 2, "cherry" : 3}
        fname = "testJSON"
        fileWriter.mapToJSON(fname, map)
        output = fileReader.JSONtoMap(fname)
        for m in map:
            self.assertEqual(output.get(m), map.get(m))
            
if __name__ == '__main__': 
    unittest.main() 