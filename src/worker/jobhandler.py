import pika
import time
import common.utils
import bliss.saga
from threading import Thread



class Job_handler(Thread):
    def __init__(self, job_description):
        super(Job_handler, self).__init__()
        print job_description
        self.job_description = common.utils.dict_to_description(job_description)
        print self.job_description
        
    def run(self):
        print "START JOB"
        print self.job_description
        js = bliss.saga.job.Service("fork://localhost")
        thejob = js.create_job(self.job_description)
        thejob.run()
        thejob.wait()
        print "END JOB"
