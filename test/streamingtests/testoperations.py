import unittest
import rapidomero.streaming.operations as operations

def c(sourcefs, targetfs, sourcepath, targetpath):
    print "called c"

operations.copy = c

class TestSequenceFunctions(unittest.TestCase):
    def test_copy(self):
        operations.copy(1,2,3,4)
	print "DONE"
