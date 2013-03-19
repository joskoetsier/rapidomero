import os
import stat

class local_filesystem:
        def walk(self, path):
                return os.walk(path)
        def is_dir(self, path):
                return stat.S_ISDIR(os.lstat(path).st_mode)
        def is_file(self, path):
                return stat.S_ISREG(os.lstat(path).st_mode)
        def open(self, path, mode='r'):
                return local_file(path, mode)
        def close(self):
                print "closes connection"
        def exists(self, path):
            try:
                os.stat(path)
            except OSError, e:
                if 'No such file' in str(e):
                    return False
                raise
            else:
                return True
        def mkdir(self, path):
            os.mkdir(path, 0700)

class local_file:
        def __init__(self, path, mode='r'):
            self._file_object = open(path, mode)
        def truncate(self):
                self._file_object.truncate()
        def write(self, buf):
                self._file_object.write(buf)
        def read(self, size):
                return self._file_object.read(size)
        def close(self):
                self._file_object.close()