from comm import Commands

# Handles the interface. Graphical / web interfaces can be created by extending this class         
class TextInterface ():
    def displayOptions(self):
        print("..................")
        for c in Commands:
            print(c.value)
        print("..................")
    
    def input(self):
        return input()
    
    def output(self, m):
        print(m)
    
    def getFilePath(self, m):
        self.output(m)
        return self.input()
    
    def takeInput(self, program):
        userOption = self.input()
        if userOption == Commands.RUN.value:
            self.getFilePath("Enter the target .cfr file") 
            program.run()
            self.takeInput()
            
        elif userOption == Commands.CHECKFILE.value:
            self.getFilePath("Enter the .csv file with the params") 
            program.checkfile()
            self.takeInput()
            
        elif userOption == Commands.NODELOCK.value:
            self.getFilePath("Enter the target .cfr file") 
            self.getFilePath("Enter the .csv file with the params") 
            self.getFilePath("Enter a name for the destinatoin .cfr file") 
            program.nodelock()
            self.takeInput()
            
        elif userOption == Commands.COMPARE.value:
            self.getFilePath("Enter the first .cfr file") 
            self.getFilePath("Enter the second .cfr file") 
            program.compare()
            self.takeInput()
            
        elif userOption == Commands.HELP.value:
            self.displayOptions()
            self.takeInput()
            
        elif userOption == Commands.END.value:
            program.end()
        
        