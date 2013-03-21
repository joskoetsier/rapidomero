import saga.job
import string

"""
   Convert a saga job description to a dictionary of key-value pairs
    
    @type description: saga job description
    @param description: job description to convert
    @rtype: dict
    @return: dictionary 
    
"""
def description_to_dict(description):
    dictionary = dict()
    att_list = description.list_attributes()
    for key in att_list:
        dictionary[key] = description.get_attribute(key)
    return dictionary

#resolve variables in a dictionary. data is the dictionary,
"""
    Resolve all variables in structured data. 
    Data is a dictionary, list or string or combination of those.
    
    @type data: list, string or dict
    @param data: Input data
    @type variables: dictionary
    @param variables: dictionary name=>value where each 'name' in the data is replaced by value
    @return: data with all substrings formatted as ${variable} are substituted
    @rtype: list, string or dict
"""
def resolve(data, variables):
    if isinstance(data, list):
        return [resolve(v, variables) for v in data]
    if isinstance(data, dict):
        return dict((k, resolve(v, variables)) for k, v in data.iteritems())
    if isinstance(data, str):
        return string.Template(data).substitute(variables) 
    return data
   
"""
    Converts a dictionary to a saga job description. Keys not found in the input are
    ignored. Case insensitive.
    @param dictionary: input dictionary
    @type dictionary: dict
    @return: saga job description
    @rtype: saga job description
    
"""
def dict_to_description(dictionary):
    #lowercase all keys. Makes the config file more forgiving
    lower_dictionary = dict((k.lower(), v) for k,v in dictionary.iteritems())
    
    description = saga.job.Description()
    if (lower_dictionary.has_key("executable")):
        description.executable = lower_dictionary["executable"]
    if (lower_dictionary.has_key("output")):
        description.output = lower_dictionary["output"]
    if (lower_dictionary.has_key("error")):
        description.error = lower_dictionary["error"]
    if (lower_dictionary.has_key("arguments")):
        description.arguments = lower_dictionary["arguments"]
    if (lower_dictionary.has_key("environment")):
        description.environment = lower_dictionary["environment"]
    if (lower_dictionary.has_key("workingdirectory")):
        description.working_directory = lower_dictionary["workingdirectory"]
    if (lower_dictionary.has_key("queue")):
        description.queue = lower_dictionary["queue"]
    if (lower_dictionary.has_key("walltimelimit")):
        description.wall_time_limit = lower_dictionary["walltimelimit"]
    if (lower_dictionary.has_key("contact")):
        description.contact = lower_dictionary["contact"]        
    if (lower_dictionary.has_key("name")):
        description.name = lower_dictionary["name"]
    if (lower_dictionary.has_key("totalcpucount")):
        description.total_cpu_count = lower_dictionary["totalcpucount"]        
    if (lower_dictionary.has_key("numberofprocesses")):
        description.number_of_processes = lower_dictionary["numberofprocesses"]
    if (lower_dictionary.has_key("spmdvariation")):
        description.spmd_variation = lower_dictionary["spmdvariation"]        
    if (lower_dictionary.has_key("project")):
        description.project = lower_dictionary["project"]
    if (lower_dictionary.has_key("filetransfer")):
        description.file_transfer = lower_dictionary["filetransfer"]           
    return description

"""
    generates a unique queue name from queue config data
"""
def generate_queue_name(queue_config):
    return queue_config["queue"]+":"+queue_config["service"]["name"]