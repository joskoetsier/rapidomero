import bliss.saga.job

def description_to_dict(description):
    dictionary = dict()
    att_list = description.list_attributes()
    for key in att_list:
        dictionary[key] = description.get_attribute(key)
    return dictionary

def dict_to_description(dictionary):
    
    #lowercase all keys. Makes the config file more forgiving
    lower_dictionary = dict((k.lower(), v) for k,v in dictionary.iteritems())
    
    description = bliss.saga.job.Description()
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
        description.workingdirectory = lower_dictionary["workingdirectory"]
    if (lower_dictionary.has_key("queue")):
        description.queue = lower_dictionary["queue"]
    if (lower_dictionary.has_key("walltimelimit")):
        description.walltimelimit = lower_dictionary["walltimelimit"]
    if (lower_dictionary.has_key("contact")):
        description.contact = lower_dictionary["contact"]        
    if (lower_dictionary.has_key("name")):
        description.name = lower_dictionary["name"]
    if (lower_dictionary.has_key("totalcpucount")):
        description.totalcpucount = lower_dictionary["totalcpucount"]        
    if (lower_dictionary.has_key("numberofprocesses")):
        description.numberofprocesses = lower_dictionary["numberofprocesses"]
    if (lower_dictionary.has_key("spmdariation")):
        description.spmdariation = lower_dictionary["spmdariation"]        
    if (lower_dictionary.has_key("project")):
        description.project = lower_dictionary["project"]
    if (lower_dictionary.has_key("filetransfer")):
        description.filetransfer = lower_dictionary["filetransfer"]   
    
    print description
        
    return description
