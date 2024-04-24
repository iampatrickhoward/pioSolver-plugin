from menu import Command, PluginCommands
from inputs import InputType, Input
from global_var import solverPath
from tkinter.filedialog import askopenfilename
from easygui import *
from filePicker import local_file_picker
from nicegui import ui, Tailwind, tailwind_types
import os
import asyncio
import unittest


printConsole = False

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
            InputType.directory: self.getFolder
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
    
    def getFolder(self) -> str:
        return self.getFilePath()
    
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
        # check if input is valid
        try: 
            return arg.parseInput(input)
        except Exception as e:
            # if the user cancels the dialogue box return None
            if input is None:
                return None
            # print error message to user
            self.output(str(e))
            # get Argument again 
            self.getArgument(arg)
    
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

    def getFolder(self) -> str:
        return diropenbox()

    def displayOptions(self):
        self.output("")
    
    def output(self, message) -> None:
        msgbox(message)
    
    

class PrettyGUInterface (GUInterface):

    def __init__(self) -> None:
        super().__init__()
        dark = ui.dark_mode()
        switch = ui.switch("dark mode")
        switch.bind_value_to(dark, 'value')
        
    
    def output(self, message) -> None:
        style = Tailwind().align_self("center").margin("mt-20").font_size("3xl")
        ui.label(message).tailwind(style)

    def outputm(self, message) -> None:
        style = Tailwind().align_self("center").margin("mt-5").font_size("lg")
        ui.label(message).tailwind(style)
        
    
    async def showMenu(self) :
        with ui.dialog() as dialog, ui.row().classes('place-self-center'):
            for c in PluginCommands:
                ui.button(c.name, on_click=lambda c=c: dialog.submit(c))
                
                
        choice = await dialog
        ui.notify(f'You chose {choice.name}')
        

    async def getFilePath(self) -> str:
        result = await local_file_picker('~', multiple=True)
        ui.notify(f'You chose {result}')
    

            
    
#--------------------------------------------------------------------------------------------------
    
def main():
    style = Tailwind('self-center')
    i = PrettyGUInterface()
    
    
    i.output("Hi!")
    #i.getFilePath("Connect your piosolver executable.")
    ui.button("Start", on_click = lambda: i.showMenu())
    
    i.outputm("pick a file")
    style = Tailwind().margin('mt-5').align_self("center")
    ui.button('Choose file', on_click=lambda: i.getFilePath(), icon="folder").tailwind(style)
        
        
    ui.run()
    
if __name__ in {"__main__", "__mp_main__"}:
    #unittest.main() 
    main()

