from comm import Commands

class Program:
    
    def __init__(self, connection, interface):
        self.connection = connection
        self.interface = interface
        #maintain a mapping of the commands to the functions that run them
        self.commandMap = {Commands.RUN: self.run,
                           Commands.CHECKFILE: self.checkfile,
                           Commands.NODELOCK: self.nodelock,
                           Commands.COMPARE: self.compare, 
                           Commands.END: self.end}
        
    def start(self):
        self.interface.output("Welcome to Piosolver!")
        self.interface.displayOptions()
        self.interface.takeInput(self)    
    
    def run(self):
        self.interface.output("Running .cfr file")
        
    def checkfile(self):
        self.interface.output("Checking params file")
        
    def nodelock(self):
        self.interface.output("nodelocking")

    def compare(self):
        self.interface.output("comparhing two .cfr files")
        
    def end(self):
        # we have to explicitely close the solver process
        self.interface.output("Closing connection to solver...")
        self.connection.exit()
        self.interface.output("Done.")

        