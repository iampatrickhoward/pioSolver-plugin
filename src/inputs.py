from enum import Enum

class Extension (Enum):
    cfr = ".cfr"
    csv = ".csv"

class InputType (Enum):
    file = 1
    number = 2
    text = 3
    
    
# an input needed by the user, with accompanying prompt
class Input ():
    def __init__(self, prompt : str, type :InputType):
        self.prompt = prompt
        self.type = type

# a file input with specific extension or extensions needed from the user
class FileInput (Input):
    def __init__(self,  prompt : str, extension : Extension):
        super().__init__(prompt, InputType.file)
        self.extension = extension
    
    #checks if extension of input is one of allowed extensions
    def isValid (self, input : str):
        for e in self.extension:
            if (input.name[-1*len(e.value):]) == e.value:
                return True and super
        return False
    
# a specifically formatted .csv file with specific formatting needed from the user.
class ParamsFileInput (FileInput):
    def __init__(self, prompt: str):
        super().__init__(prompt, Extension.csv)