import yaml
import logging
import sys

logging.basicConfig(filename='logfile.txt',level=logging.DEBUG)

def get_queue_configs(path_to_config):
    if path_to_config == None:
        file_name='config.yaml'
    else:
        file_name = path_to_config
    lower_queue_configs = []
    try:
        queue_configs = yaml.load(open(file_name, "r"))   
 
        #recusively lower case keys
        def lower_keys(inp):
            if isinstance(inp, list):
                return [lower_keys(v) for v in inp]
            if isinstance(inp, dict):
                return dict((k.lower(), lower_keys(v)) for k, v in inp.iteritems())
            return inp
    
        #lowercase all keys. Makes the config file more forgiving
        lower_queue_configs = lower_keys(queue_configs)
        
    except IOError:
        logging.error("Could not open configuration file: "+ file_name) 
        print "Could not find config.yaml at "+file_name   
        sys.exit()
    except yaml.scanner.ScannerError, messg:
        logging.error("Error parsing config file")
        logging.error(messg)
    return lower_queue_configs
