import yaml
import logging

logging.basicConfig(filename='logfile.txt',level=logging.DEBUG)

class config:
    context = 0
    job_description = 0
    host_url = 0
    cluster_type = 0
    def __init__(self, file_name):
        try:
            fd = open(file_name, "r")
            self._config_dict = yaml.load(fd)
        except IOError:
            logging.error("Could not open configuration file: "+file_name)    
        except yaml.scanner.ScannerError, messg:
            logging.error("Error parsing config file")
            logging.error(messg)
    
    def get_config(self):
        return self._config_dict
