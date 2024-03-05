import unittest
from interface import *
from program import *
from comm import CommandList


class Tests(unittest.TestCase):
    
    def testCommandDispatcher(self):
        p = Program(Solver(), TextInterface())
        function = p.commandDispatcher[CommandList.RUN]
        function(["hi.cfr"])

if __name__ == '__main__': 
    unittest.main() 