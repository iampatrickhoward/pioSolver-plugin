import sys
import os
from SolverConnection.solver import Solver
from interface import TextInterface, GUInterface
from program import Program

def main():
    interface = TextInterface()
    # starts the solver process using the provided .exe path
    # solverPath = interface.getFilePath()
    
    solverPath = "C:\PioSOLVER\PioSOLVER3-pro.exe"
    connection = Solver(solverPath)
    # report success
    interface.output("Solver connected successfully! Welcome to PioSolver")
    # The comment `# report success` is indicating that the following line of code is intended to
    # report the successful connection of the solver. In this case, the line `interface.output("Solver
    # connected successfully")` is likely meant to display a message in the user interface indicating
    # that the solver has been connected successfully.
    # now let's use created solver connection to call some commands
    program = Program(connection, interface)
    program.run(["C:\\" + "Users\degeneracy station\Documents\PioSolver-plugin\As5h3s.cfr"])
    program.start()
    

def example(connection):
    cfr = ""
    # call and print the result of "show metadata" on the provided .cfr file
    metadata = connection.command(line =f"show_metadata {sys.argv[2]}")
    print_lines(metadata)

    # load the tree
    output = connection.command(line=f"load_tree {sys.argv[2]}")
    print_lines(output)

    # show hands order (solver will return always the same answer)
    handorder = connection.command("show_hand_order")
    print_lines(handorder)
    
    # show ranges
    print("Range OOP:")
    range = connection.command("show_range OOP r")
    print_lines(range)

    print("Range IP:")
    range = connection.command("show_range IP r")
    print_lines(range)

    # calculate EV
    calcevOOP = connection.command("calc_ev OOP r:0")
    print("EV IP:")
    print_lines(calcevOOP)

    # we have to explicitely close the solver process
    print("Closing connection:")
    connection.exit()
    print("Connection closed.")
    print('Done.')



def print_lines(lines):
    for line in lines:
        print(line)

if __name__ == "__main__":
    main()


