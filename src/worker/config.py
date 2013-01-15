import yaml
import logging

logging.basicConfig(filename='logfile.txt',level=logging.DEBUG)

class config:
    context = 0
    job_description = 0
    host_url = 0
    cluster_type = 0
    
    def read_config(self, file_name):
        try:
            fd = open(file_name, "r")
        except IOError:
            logging.error("Could not open configuration file: "+file_name)
        
        config_dict = yaml.load(fd)