import unittest
from interface import *
from comm import *
from program import*
from SolverConnection.solver import*

class Tests(unittest.TestCase):
    def testCommandMap(self):      
        c = Command ("run", {FileInput (Extension.cfr, "Pick a .cfr file to run")})
        self.assertEqual(c.__str__(), "run") 

if __name__ == '__main__': 
    unittest.main() 