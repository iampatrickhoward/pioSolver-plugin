from enum import Enum
from mypy import Callable
from fileIO import fileWriter, fileReader
import os
class Extension (Enum):
    cfr = ".cfr"
    csv = ".csv"
    json = ".json"
    # folders have no extension
    folder = ""

class InputType (Enum):
    file = 1
    number = 2
    text = 3
    
# an input needed by the user, with accompanying prompt
class Input ():
    def __init__(self, type : InputType, prompt : str) :
        self.prompt = prompt
        self.type = type
            
    # checks if is valid input
    def isValid (self, input: str) -> bool:
        return True
    
    def readInput (self, input: str):
        if self.isValid(input) :
            return input

# a file input with specific extension or extensions needed from the user
class FileInput (Input):
    def __init__(self, extension : Extension, prompt : str):
        super().__init__(InputType.file, prompt)
        self.extension : str = extension.value
    
    def isCorrectExtension (self, fName : str) :
        # if last few letters of file name equals the extension this input is supposed to have, return true
        if (fName[-1*len(self.extension):]) == self.extension:
                return True
        return False
    
    # check if file type is correct, if so return
    def readInput(self, input : str) :
        if self.isCorrectExtension(input):
            return input
        raise Exception("Wrong file type. Select another file.")


class FolderOf (FileInput) :
    
    # check if file type is correct, if so return
    def readInput(self, input : str) -> dict[str, int] :
        allFilesInside : list [str] = []
        try: 
            allFilesInside = os.listdir(input)
        except: 
            raise Exception("Please select a valid folder")
        neededFiles = []
        # return the files inside the folder which match the needed extension
        for f in allFilesInside:
            if self.isCorrectExtension(f):
                neededFiles.append(f)
        if not neededFiles:
            raise Exception("Folder has no " + self.extension + " files")
        return neededFiles
    
class WeightsFile (FileInput):
    def __init__(self, prompt: str):
        super().__init__(Extension.json, prompt)
    
    # the interface gets a file name from the reader
    def readInput(self, input : str) -> dict[str, int] :
        input = super().readInput(input)
        weightMap = fileReader.JSONtoMap(map)
        
        
        
# a specifically formatted .csv file with specific formatting needed from the user.
class BoardFile(FileInput):
    def __init__(self, prompt: str):
        super().__init__(Extension.json, prompt)
    
