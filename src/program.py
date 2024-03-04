from comm import CommandList, Command

class Program:
    
    def __init__(self, connection, interface):
        self.connection = connection
        self.interface = interface
        #maintain a mapping of the commands to the functions that run them
        self.commandDispatcher = {CommandList.RUN: self.run,
                                  CommandList.CHECKFILE: self.checkfile,
                                  CommandList.NODELOCK: self.nodelock,
                                  CommandList.COMPARE: self.compare, 
                                  CommandList.END: self.end,
                                  CommandList.HELP: self.help}
        
    def start(self):
        self.interface.output("Welcome to Piosolver!")
        self.interface.displayOptions()
        self.takeInput()    
        
        
    def runCommand(self, command : Command, args):
        self.commandDispatcher[command](args)
    
    def takeInput(self):
        inputtedCommand = self.interface.getCommand()
        inputtedArgs = self.interface.getCommandArgs(inputtedCommand)
        self.runCommand(inputtedCommand, inputtedArgs)
        if (inputtedCommand != CommandList.END):
            self.takeInput()
        
    def run(self, args):
        self.interface.output("Running .cfr file")
        
    def checkfile(self, args):
        self.interface.output("Checking params file")
        
    def nodelock(self, args):
        self.interface.output("nodelocking")

    def compare(self, args):
        self.interface.output("comparhing two .cfr files")
    
    def help(self, args):
        # we have to explicitely close the solver process
        self.interface.displayOptions()
        
    def end(self, args):
        # we have to explicitely close the solver process
        self.interface.output("Closing connection to solver...")
        self.connection.exit()
        self.interface.output("Done.")

        