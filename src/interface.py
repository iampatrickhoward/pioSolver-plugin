from comm import *
from inputs import *

# Handles the interface. Graphical / web interfaces can be created by extending this class    
class Interface ():
    def __init__(self) -> None:
        self.commandMap = {}
        for command in CommandList:
            self.commandMap[command.__str__()] = command
            
        self.inputGetterMap = {InputType.file : self.getFilePath,
                      InputType.text : self.getText,
                      InputType.number : self.getText}
    
class TextInterface (Interface):
    
    def __init__(self) -> None:
        super().__init__()
        
    def displayOptions(self):
        print("..................")
        for c in CommandList:
            print(c.name)
        print("..................")
    
    
    #gets a Command from user
    def getCommand(self) -> Command:
        self.output("Enter a command")
        input = self.getText()
        print(self.commandMap.keys())
        if input not in self.commandMap.keys():
            self.output("Invalid input. Type 'help' for a list of commands.")
            self.getCommand()
        else:
            return self.commandMap[input]
            
    def getCommandArgs(self, command) :
        userInputs = {}
        for arg in command.args:
            #output the prompt
            self.output(arg.prompt)
            #run the function correspondong to the input type
            userInputs.append(self.inputGetterMap(arg.type)())
        return userInputs
        
    #gets a text input from user 
    def getText(self) -> str:
        return input()
    
    #gets a file path
    def getFilePath(self) -> str:
        return input()
    
    def output(self, message) -> None:
        print(message)

        