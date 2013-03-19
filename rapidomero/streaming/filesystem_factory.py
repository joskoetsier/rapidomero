import urlparse
import sftpfilesystem
import localfilesystem

def get_filesystem(url, username=None, password=None, key_filename=None):
    parsed_url = urlparse.urlparse(url)
    if parsed_url.scheme=="sftp":
        return sftpfilesystem.sftp_filesystem(parsed_url.netloc, username, password, key_filename)
    if parsed_url.scheme=="file":
        return localfilesystem.local_filesystem()
    
