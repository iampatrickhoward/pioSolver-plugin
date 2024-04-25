from __future__ import annotations
import sys
from SolverConnection.solver import Solver
from interface import GUInterface
from global_var import solverPath
from program import Program


def main():
    interface = GUInterface()
    # starts the solver process using the provided .exe path
    # solverPath = interface.getFilePath()
    
    #interface.output("Link your file executable")
    #solverPath = interface.getFilePath()
    
    if(solverPath):
        connection = Solver(solverPath)
        # report success
        interface.output("Solver connected successfully! Welcome to PioSolver")
        # The comment `# report success` is indicating that the following line of code is intended to
        # report the successful connection of the solver. In this case, the line `interface.output("Solver
        # connected successfully")` is likely meant to display a message in the user interface indicating
        # that the solver has been connected successfully.
            # now let's use created solver connection to call some commands
        program = Program(connection, interface)
        program.start()

if __name__ == "__main__":
    main()


