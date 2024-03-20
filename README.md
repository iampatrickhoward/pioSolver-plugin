# PioSolver Plugin
This plugin builds an interface that starts the solver process and communicates with PioSolver to streamline the running of poker simulations.

You can communicate with the Piosolver interface using command line arguments following UPI (universal poker interface) notation. The documentation of the PioSolver interface can be found here:
https://piofiles.com/docs/upi_documentation/

## Requirements

* Install Python version at least 3.6.
* For development, I highly encourage installing mypy for typechecking

### Running the code

1) Open PowerShell or Command Prompt (Windows + R, then type "cmd" and click "OK") 
2) Run "python start.py"

## Structure
* comm.py has classes Command and the enum PluginCommand, which contains a list of all the commands the plugin has. 
* interface.py has the class Interface and its child classes TextInterface and GUInterface. It handles all UI aspects of the plugin
* inputs.py has enums InputType (the different kinds of inputs the user can enter, for the purpose of telling the interface how to get the input) and Extension (stores strings for different extensions). It also has the class Input, which represents an input the user might need. An Input has a type and an isValid function.




* interface.py

# Adding New Commands to Plugin
1) Add an member to the enum PluginCommands(comm.py)
2) Create a method in the class Program (program.py) that conveys the command line arguments to the PioSolver executable
3) Add an entry to the commandDispatcher dictionary in the class Program(program.py)




