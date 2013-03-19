import posixpath
import filesystem_factory
import urlparse
    
def copy_file(sourcefs, targetfs, sourcepath, targetpath):
    bufmax = 1024*50
    source_file = sourcefs.open(sourcepath)
    target_file = targetfs.open(targetpath, 'w')
    buf = source_file.read(bufmax)
    while(buf!=""):
        target_file.write(buf)
        buf = source_file.read(bufmax)
        
def copy_file_into_directory(sourcefs, targetfs, sourcepath, targetpath):
    #get filename
    file_name = (posixpath.split(sourcepath))[1]
    copy_file(sourcefs, targetfs, sourcepath, posixpath.join(targetpath, file_name))

def recursive_copy(sourcefs, targetfs, sourcepath, targetpath):
    #normalise paths
    norm_sourcepath = posixpath.normpath(sourcepath)
    norm_targetpath = posixpath.normpath(targetpath)
    
    #Create the first directory in the target file system if it does not already exist
    source_end_path = posixpath.split(posixpath.normpath(sourcepath))[1]
   
    #if the target path exists, make a new directory into the target path directory
    if targetfs.exists(norm_targetpath):
        base_target_path = posixpath.normpath(posixpath.join(norm_targetpath, source_end_path)) 
    #if the target does not exist but its parent does, rename the directory and copy
    elif targetfs.exists(posixpath.normpath(posixpath.join(norm_targetpath, ".."))):
        #If it does not exist, create that directory
        base_target_path = norm_targetpath
    else:
        raise IOError("Cannot copy into target: "+targetpath)

    if not targetfs.exists(base_target_path):
        targetfs.mkdir(base_target_path)
              
    for (path, directories, files) in sourcefs.walk(norm_sourcepath):
        rel_source_path = posixpath.relpath(path, norm_sourcepath)
        new_target_path = posixpath.normpath(posixpath.join(base_target_path, rel_source_path))
        print new_target_path
        for f in files:
            copy_file_into_directory(sourcefs, targetfs, posixpath.join(path, f), new_target_path)
        for d in directories:
            new_directory = posixpath.join(new_target_path, d)
            if not targetfs.exists(new_directory):
                targetfs.mkdir(new_directory)

def copy(sourcefs, targetfs, sourcepath, targetpath):
    #Source should exist
    if (not sourcefs.exists(sourcepath)):
        raise IOError("Source does not exist! "+sourcepath)
    #Source is a file and target is a file or does not exist
    if (not targetfs.exists(targetpath) or targetfs.is_file(targetpath)) and  sourcefs.is_file(sourcepath):
        copy_file(sourcefs, targetfs, sourcepath, targetpath)
    #Source is a directory and target is a directory or does not exist
    elif (not targetfs.exists(targetpath) or targetfs.is_dir(targetpath)) and sourcefs.is_dir(sourcepath):
        recursive_copy(sourcefs, targetfs, sourcepath, targetpath)
    #Source is a file and target is a directory. Directory should exist
    elif sourcefs.is_file(sourcepath) and targetfs.exists(targetpath) and targetfs.is_dir(targetpath):
        copy_file_into_directory(sourcefs, targetfs, sourcepath, targetpath)
    else:
        raise IOError("cannot copy to a directory")
    
def copy_urls(sourceurl, targeturl, sourcectx, targetctx):
    sourcefs = filesystem_factory.get_filesystem(sourceurl, username=sourcectx.username, password=sourcectx.password, key_filename=sourcectx.key_filename)
    targetfs = filesystem_factory.get_filesystem(targeturl, username=targetctx.username, password=targetctx.password, key_filename=targetctx.key_filename)
    sourceurl_parsed = urlparse.urlparse(sourceurl)
    targeturl_parsed = urlparse.urlparse(targeturl)
    copy(sourcefs, targetfs, sourceurl_parsed.path, targeturl_parsed.path)