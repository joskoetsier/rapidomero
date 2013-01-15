import pika
import time
import common.utils
import bliss.saga
from config import config
from threading import Thread
import logging



class Job_handler(Thread):
    def __init__(self, job_description):
        super(Job_handler, self).__init__()
        
        #Get job description and config
        self._job_description = job_description
        self._config = config("config.yaml")
        
        logging.log(logging.DEBUG, self._job_description)
        logging.log(logging.DEBUG, self._config)
        
        #overwrite job description with the one found in the config file
        self._job_description.update(self._config.get_config()["job"])     
    def run(self):
        
       
        print "START JOB"
        print self._job_description
        js = bliss.saga.job.Service("fork://localhost")
        thejob = js.create_job(common.utils.dict_to_description(self._job_description))
        thejob.run()
        thejob.wait()
        print "END JOB"
