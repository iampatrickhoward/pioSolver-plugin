from comm import Command, PluginCommands
from inputs import InputType, Input
from tkinter.filedialog import askopenfilename
from easygui import *
import os

# Handles the interface. Graphical / web interfaces can be created by extending this class
def clearConsole():
    os.system('cls' if os.name=='nt' else 'clear')
class Interface:
    def __init__(self) -> None:
        self.commandMap: dict[str, Command] = {}
        for enumMember in PluginCommands:
            self.commandMap[enumMember.value.__str__()] = enumMember

        self.inputGetterMap = {
            InputType.file: self.getFilePath,
            InputType.text: self.getText,
            InputType.number: self.getText,
        }

    # displays possible commands
    def displayOptions(self):
        print("..................")
        for c in PluginCommands:
            print(c.name)
        print("..................")

    # gets a text input from user
    def getText(self) -> str:
        return input()

    # gets a file path
    def getFilePath(self) -> str:
        return input()
    
    # output message
    def output(self, message) -> None:
        print(message)
        


class TextInterface(Interface):
    def __init__(self) -> None:
        super().__init__()

    # gets a Command from user
    def getCommand(self) -> PluginCommands:
        self.output("Enter a command")
        input = self.getText()
        if input not in self.commandMap.keys():
            self.output("Invalid input. Type 'help' for a list of commands.")
            return self.getCommand()
        else:
            return self.commandMap[input]

    def getArgument(self, arg : Input) -> str:
        # output the prompt
        self.output(arg.prompt)
        # call the function that retrieves this type of argument
        input = self.inputGetterMap[arg.type]()
        if (arg.isValid(input)):
            return input
        else:
            self.output("That's not a valid input, try again!")
            return self.getArgument(arg)
    
    def getCommandArgs(self, command: Command) -> list[str] :
        userInputs = []
        for whichArg in command.args:
            input = self.getArgument(whichArg)
            if input is None:
                return None
            userInputs.append(input)
        return userInputs

    
class GUInterface(TextInterface):
    
    def __init__(self) -> None:
        super().__init__()
    
    def getText(self) -> str:
        return enterbox("", "", "")
    
    def getCommand(self) -> PluginCommands:
        input = choicebox("Pick a command", "Menu", self.commandMap.keys()) 
        if (input is None):
            return PluginCommands.END
        return self.commandMap[input]

    # gets a file path
    def getFilePath(self) -> str:
        return fileopenbox()

    def displayOptions(self):
        self.output("")
    
    def output(self, message) -> None:
        msgbox(message)
    
    def openFileDialogue (self) -> str:
        filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
        return filename