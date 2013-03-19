import abstractfilesystem
import os
import stat
import paramiko

class sftp_filesystem(abstractfilesystem.abstract_filesystem):
        def __init__(self, host, username, password, key_filename=None):
            self._ssh = paramiko.SSHClient()
            #self._ssh.get_transport().use_compression(compress=True)
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(host, username=username, password=password, key_filename=key_filename)  
            self._client = self._ssh.open_sftp()
 
        def walk(self, path):
            p=path
            files=[]
            folders=[]
            for f in self._client.listdir_attr(path):
                if stat.S_ISDIR(f.st_mode):
                    folders.append(f.filename)
                else:
                    if stat.S_ISREG(f.st_mode):
                        files.append(f.filename)
            yield path,folders,files
            for folder in folders:
                new_path=os.path.join(p,folder)
                for x in self.walk(new_path):
                    yield x

        def is_file(self, path):
                return stat.S_ISREG(self._client.lstat(path).st_mode)
        def is_dir(self, path):
                return stat.S_ISDIR(self._client.lstat(path).st_mode)
            
        def open(self, filename, mode='r'):
                return sftp_file(self._client, filename, mode=mode)
        def close(self):
                self._client.close()
                self._ssh.close()
        def exists(self, path):
            try:
                self._client.stat(path)
            except IOError, e:
                if 'No such file' in str(e):
                    return False
                raise
            else:
                return True

        def mkdir(self, path):
                self._client.mkdir(path, 0700)

                
class sftp_file:
        def __init__(self, client, path, mode='r'):
            self.client=client
            self._fileobject = client.file(path, mode);
        def truncate(self):
                self._fileobject.truncate(0);
        def write(self, buf):
                self._fileobject.write(buf)
        def read(self, size):
                return self._fileobject.read(size)
        def close(self):
            self._fileobject.close()
    
