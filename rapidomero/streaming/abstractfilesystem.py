class abstract_filesystem:
        def walk(self, path):
                print "return walk-like structure"
        def is_file(self, path):
                print "is file"
        def is_dir(self, path):
                print "is dir"
        def open(self, path, mode='r'):
                print "get abstract file"
        def close(self):
                print "closes connection"
        def exists(self, path):
                print "does the path exist?"
        def mkdir(self, path):
                print "make a directory"


class abstract_file:
        def truncate(self):
                print "empty file"
        def write(self, buf):
                print "appends to file"
        def read(self, size):
                print "reads buffer"
            
            
    