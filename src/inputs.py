from enum import Enum

class Extension (Enum):
    cfr = ".cfr"
    csv = ".csv"
    json = ".json"

class InputType (Enum):
    file = 1
    number = 2
    text = 3
    
# an input needed by the user, with accompanying prompt
class Input ():
    def __init__(self, type : InputType, prompt : str):
        self.prompt = prompt
        self.type = type
    
    def isValid (self, input: str) -> bool:
        return True

# a file input with specific extension or extensions needed from the user
class FileInput (Input):
    def __init__(self, extension : Extension, prompt : str):
        super().__init__(InputType.file, prompt)
        self.extension : Extension = extension
    
    #checks if extension of input is one of allowed extensions
    #checks list of extensions in case add ability for input to be of multiple file types in future
    def isValid (self, input : str) -> bool :
        validExtensions : list[Extension] = [self.extension]
        for e in validExtensions:
            if (input[-1*len(e.value):]) == e.value:
                return True
        return False
    
# a specifically formatted .csv file with specific formatting needed from the user.
class ParamsFileInput (FileInput):
    def __init__(self, prompt: str):
        super().__init__(Extension.csv, prompt)