from SolverConnection.solver import Solver

def parseOutputToList(strOutput : str) -> list[str]:
    # delimit pioSolver output using whitespace
    output : list[str] = strOutput.split("  ")
    # strip of colons and additional whitespace
    for i in range(0, len(output)):
        output[i] = output[i].strip(": ")
        if output[i].isnumeric():
            output[i] = float(output[i])
    return output

def parseStringToList(strOutput : str) -> list[str]:
    # delimit pioSolver output using whitespace
    output : list[str] = strOutput.split(" ")
    # strip of colons and additional whitespace
    for i in range(0, len(output)):
        output[i] = output[i].strip()
        if output[i].isnumeric():
            output[i] = float(output[i])
    return output

# turns list into a string to feed into Pio
def makeString(elems : list[type]) -> str:
    strInput = ""
    for i in elems:
        strInput = strInput + " " + i.__str__()
    return strInput
