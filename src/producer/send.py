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
        
        
    def send_job(self, variables):
        
        jobid = str(uuid.uuid1())
        
        yaml_string = yaml.dump(variables)
        
        #Open connection
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(self._queue_config["host"]))
    
        #Open channel
        self._channel = self._connection.channel()
    
        #Declare the job queue
        self._channel.queue_declare(queue=self._queue_config["queue"], durable=True, exclusive=False, auto_delete=False)
    
        #Send to default exchange for 'jobs' queue
        self._channel.basic_publish(exchange='', routing_key=self._queue_config["queue"], body=yaml_string, 
                                    properties=pika.BasicProperties(reply_to=jobid) )
        
        return jobid
      
        
    def consume_status(self, jobid, callback):    
        self._channel.queue_declare(queue=jobid, auto_delete=True)
  
        def _callback(ch, method, properties, body):   
            callback(body) 
            if (body.find("Done")!=-1 or body.find("Failed")!=-1):
                ch.basic_cancel( self._consumer_tag )
        
        self._consumer_tag= self._channel.basic_consume(_callback, queue=jobid, no_ack=True)
        
        self._channel.start_consuming()
        self._connection.close()
