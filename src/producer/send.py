import pika 
import sys
import logging
import yaml
import bliss.saga.job
import common.utils
import uuid
from common.constants import Constants

logging.basicConfig()

class sender:

    def __init__(self, queue_config):
        self._queue_config = queue_config
        
        
    def send_job(self, job_description):
        
        self._job_description = job_description
        self._reply_to = str(uuid.uuid1())
        
        dictionary = common.utils.description_to_dict(job_description)
        yaml_string = yaml.dump(dictionary)
        
        #Open connection
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(self._queue_config["host"]))
    
        #Open channel
        self._channel = self._connection.channel()
    
        #Declare the job queue
        self._channel.queue_declare(queue=self._queue_config["queue"], durable=True, exclusive=False, auto_delete=False)
    
        #Send to default exchange for 'jobs' queue
        self._channel.basic_publish(exchange='', routing_key=self._queue_config["queue"], body=yaml_string, 
                                    properties=pika.BasicProperties(reply_to=self._reply_to) )
      
        
    def consume_status(self, callback):    
        self._channel.queue_declare(queue=self._reply_to)
  
        def _callback(ch, method, properties, body):   
            callback(body) 
            if body.find("Done")!=-1:
                ch.basic_cancel( self._consumer_tag )
        
        self._consumer_tag= self._channel.basic_consume(_callback, queue=self._reply_to, no_ack=True)
        
        self._channel.start_consuming()
        self._connection.close()
