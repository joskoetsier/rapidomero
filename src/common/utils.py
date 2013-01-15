import bliss.saga.job

def description_to_dict(description):
    dictionary = dict()
    att_list = description.list_attributes()
    for key in att_list:
        dictionary[key] = description.get_attribute(key)
    return dictionary

def dict_to_description(dictionary):
    description = bliss.saga.job.Description()
    for key, value in dictionary.iteritems():
        description.set_attribute(key,value)
    return description
