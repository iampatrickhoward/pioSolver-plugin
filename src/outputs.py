import csv
import json

class fileWriter():

    def mapToCSV(fname, map) -> None:
        with open(fname, 'w+', newline='') as file:
            w = csv.writer(file)
            for m in map:
                w.writerow([m, map[m]])

    def mapToJSON(fname, map):
        with open(fname, "w+") as file:
            json.dump(map, file)