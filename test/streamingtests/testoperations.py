import unittest
import streaming.operations

def c(sourcefs, targetfs, sourcepath, targetpath):
    print "called c"

streaming.operations.copy = c

class TestSequenceFunctions(unittest.TestCase):
    def test_copy(self):
        streaming.operations.copy(1,2,3,4)
	print "DONE"
