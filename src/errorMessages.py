

class Errors():
    
    # nodeIDErrors
    @staticmethod
    def invalid_node (nodeID : str):
        return nodeID + " is not a valid node!" 
    
    
    # File selection errors.
    
    @staticmethod
    def noFilesinFolder (extension : str):
        return "Folder has no " + extension + " files. "
    
    @staticmethod
    def wrongFileType (extension : str):
        return "This file does not have type " + extension + ". "
    invalidFile = "Invalid file. "
    invalidFolder = "Please select a valid folder. "

    # board JSON format  errors
    noDecisionLineError = "There needs to be an entry of the form: \"all\" : \"r:0:...\". This entry designates the overall decision tree used for all .cfr files in the list."
    noRootNode = "The node ID needs to start with a valid root node \"r:0\""
    needsSpecificFileInfo = "This board file has turn or river nodes or bets of unspecfied size. You need to add rows that specify these for each .cfr file."
    nonNumericBetError = "Bet size needs to be numeric."
    # weights JSON format errors
    
    @staticmethod
    def invalidCategory (category : str):
        return "JSON file with category weights not valid - "  + category + " is neither a hand nor a draw category"
    
    @staticmethod
    def noNegativeWeights (category : str):
        return "Invalid weight for " + category + ". Only exception categories can have negative weights."
    
   
    

