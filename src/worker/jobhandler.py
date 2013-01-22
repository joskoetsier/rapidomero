import pika
import time
import common.utils
import bliss.saga as saga
from threading import Thread
import logging

class Job_handler(Thread):
    def __init__(self, queue_config, job_description, reply_to):
        super(Job_handler, self).__init__()
        
        self._queue_config = queue_config
        self._job_description = job_description
        self._reply_to = reply_to
        
        logging.log(logging.DEBUG, self._job_description)
        logging.log(logging.DEBUG, queue_config)
        print queue_config
        
        #overwrite job description with the one found in the config file
        self._job_description.update(self._queue_config["job"])    
        
    
         
    def run(self):

        service = self._queue_config["service"]
        connection_method = service["connection"] #either local, ssh or gsissh
        resource = service["resource"] #either fork, pbs, torque
        host = service["host"]
        
    
        #if a connection is local omit it in the URL i.e. pbs://127.0.0.1 or sge://127.0.0.1
        #if a resource is "fork" AND non-local, omit the fork. i.e. ssh://127.0.0.1 or gsissh://127.0.0.1
        #if a resource is non-local and not fork append with a +. i.e. pbs+ssh://127.0.0.1
        if (connection_method=="local" or connection_method==None):
            connection_method = ""                          
        else:
            if resource == "fork":
                resource = ""
            else:
                resource = resource+"+"
                
        url = resource+connection_method+"://"+host       
        
        #Fill in security context
        ctx = saga.Context()
        if (connection_method=="SSH" or connection_method=="GSISSH"):
            ctx.type = saga.Context.SSH
            ctx.userid  = service["userid"] # your identity on the remote machine
            ctx.userkey = service["userkey"] # ssh key to use (only necessary if in non-default location)

        ses = saga.Session()
        ses.contexts.append(ctx)
        
        #create job
        js = saga.job.Service(url,session=ses)
        thejob = js.create_job(common.utils.dict_to_description(self._job_description))
        thejob.run()
        
        #create the reply_to queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(self._queue_config["host"]))
        channel = connection.channel()
               
        #send the state as soon as it has changed. Poll
        polling_time = self._queue_config["pollingtime"]
        
        jobstate = thejob.get_state()
        newjobstate = jobstate
        message = ' * Job %s status: %s' % (thejob.jobid, jobstate)
        channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)
                     
        while jobstate is not saga.job.Job.Done:          
            while jobstate==newjobstate:
                time.sleep(polling_time)
                newjobstate = thejob.get_state()        
            jobstate = newjobstate 
            message = ' * Job %s status: %s' % (thejob.jobid, jobstate)
            channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)  
            
        channel.close()
        connection.close()         
        print "END JOB"
