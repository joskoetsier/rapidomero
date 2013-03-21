class abstract_filesystem:
        """
            function similar to 'walk' in os.walk.
            @param path: path to start the walk
            @return: see os.walk 
        """
        def walk(self, path):
                print "return walk-like structure"
                
        """
            @return: true, if the object referred to by path is a 'file', false otherwise
        """
        def is_file(self, path):
                print "is file"
        """
            @return: true, if the object referred to by path is a 'directory', false otherwise
        """
        def is_dir(self, path):
                print "is dir"
        """
            Opens a file. 
        """
        def open(self, path, mode='r'):
                print "get abstract file"
        """
            Closes the file
        """
        def close(self):
                print "closes connection"
        """
            @return true, if the path exists
        """
        def exists(self, path):
                print "does the path exist?"
        """
            makes a directory at the path specified
        """
        def mkdir(self, path):
                print "make a directory"


class abstract_file:
        """
            empties the file
        """
        def truncate(self):
                print "empty file"
        """
            writes 'buf' to the file
        """
        def write(self, buf):
                print "appends to file"
        """
            reads at most 'size' bytes.
        """
        def read(self, size):
                print "reads buffer"
            
            
    