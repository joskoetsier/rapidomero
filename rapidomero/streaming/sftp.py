import os
import paramiko

def list_dir(method, path):
    print method.listdir(path);
    
