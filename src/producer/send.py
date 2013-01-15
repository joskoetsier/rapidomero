import pika 
import sys
import logging
import yaml
import bliss.saga.job
import common.utils
from common.constants import Constants

logging.basicConfig()


def send_job(job_description, host='localhost'):

    dictionary = common.utils.description_to_dict(job_description)
    yaml_string = yaml.dump(dictionary)
    print yaml_string
    #Open connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))

    #Open channel
    channel = connection.channel()

    #Declare the job queue
    channel.queue_declare(queue=Constants.job_queue,durable=True, exclusive=False, auto_delete=False)

    #Send to default exchange for 'jobs' queue
    channel.basic_publish(exchange='', routing_key=Constants.job_queue, body=yaml_string)
  
    connection.close()
