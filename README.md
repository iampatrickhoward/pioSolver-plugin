# PioSolverConnection
Examples on how to communicate with PioSolver in different languages

The example code shows how to start a solver process and how to send commands and parse responses from PioSolver. 
The documentation of the PioSolver interface can be found here:
https://piofiles.com/docs/upi_documentation/

# Python
 
### Requirements

* Install Python version at least 3.6.
* For development, I highly encourage installing mypy for typechecking

### Running the code

Example file connects to the solver and requests some data from a specified save file.

1) Open PowerShell or Command Prompt (Windows + R, then type "cmd" and click "OK") 
2) run "python start.py"
3) Try running command: ` python runme.py <path_to_solver> <path_to_tree> `

## Structure
* 

# Adding New Commands to Plugin
1) Add an member to the enum PluginCommands(comm.py)
2) Create a method in the class Program (program.py) that conveys the command line arguments to the PioSolver executable
3) Add an entry to the commandDispatcher dictionary in the class Program(program.py)




