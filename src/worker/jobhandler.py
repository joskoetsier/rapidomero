import pika
import time
import yaml
import common.utils
import bliss.saga as saga
from threading import Thread
import logging

class Job_handler(Thread):
    def __init__(self, queue_config, variables, reply_to, event):
        super(Job_handler, self).__init__()
        
        self._queue_config = common.utils.resolve(queue_config, variables)
        print self._queue_config
        self._reply_to = reply_to
        self._event = event
        self._queue_name = self._queue_config.get("queue")
        self._queue_host = self._queue_config.get("host")
        self._job = self._queue_config.get("job")
        self._service = self._queue_config.get("service")
        self._files = self._queue_config.get("files")
                
        logging.log(logging.DEBUG, queue_config)
                
    def run(self):
        if self._job is not None and self._service is not None:
            self.do_job()
        if self._files is not None:
            for f in self._files:
                self.do_file(f) 

    def do_file(self, file_element):
        print file_element
        source = file_element.get("source")
        target = file_element.get("target")
        
        def buildctx(transfer):
            ctx = saga.Context()
            if transfer.get("userid") is not None:
                ctx.userid  = transfer.get("userid") # your identity on the remote machine
            if transfer.get("userkey") is not None:
                ctx.userkey = transfer.get("userkey") # ssh key to use (only necessary if in non-default location)
            if transfer.get("url").lower().startswith("gsiftp"):
                ctx.type = saga.Context.GSISSH
            if transfer.get("url").lower().startswith("sftp"):
                ctx.type = saga.Context.SSH
                
            return ctx
        
        ses = saga.Session()
        ses.contexts.append(buildctx(source))
        #ses.contexts.append(buildctx(target))
        
        out = saga.filesystem.File(source.get("url"), session=ses)
        out.copy(target.get("url"))

         
    def do_job(self):
        connection_method = self._service["connection"] #either local, ssh or gsissh
        resource = self._service["resource"] #either fork, pbs, torque
        host = self._service["host"]    
        
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
            ctx.userid  = self._service["userid"] # your identity on the remote machine
            ctx.userkey = self._service["userkey"] # ssh key to use (only necessary if in non-default location)

        ses = saga.Session()
        ses.contexts.append(ctx)
        
        #create job 
        jobstate = None
        reply = dict()     
        try:          
            js = saga.job.Service(url,session=ses)
            thejob = js.create_job(common.utils.dict_to_description(self._job))
            thejob.run()
            print "Started Job: "
            print self._job
            jobstate = thejob.get_state()
            reply["message"] = None
            reply["status"] =  str(jobstate)
        except saga.Exception as ex:
            print "Exception thrown"
            print str(ex)
            reply["message"] = ex.message
            reply["status"] = str(saga.job.Job.Failed)    
        finally:
            reply["jobid"] = str(thejob.jobid)
            
        #create the reply_to queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(self._queue_host))
        channel = connection.channel()
        #passive=False, durable=False, exclusive=False, auto_delete=False, nowait=False, arguments=None
        #channel.queue_declare(queue=self._reply_to, durable=False, exclusive=False, auto_delete=True)
        thejob.wait(-1)  
        #send the state as soon as it has changed. Poll
        polling_time = self._service["pollingtime"]
        
        message = yaml.dump(reply)
        channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)
         
        newjobstate = jobstate            
        while jobstate is not saga.job.Job.Done and jobstate is not saga.job.Job.Failed:          
            while jobstate==newjobstate:
                time.sleep(polling_time)
                newjobstate = thejob.get_state()        
            jobstate = newjobstate 
            reply["message"] = ""
            reply["status"] =  str(jobstate)
            message = yaml.dump(reply)
            channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)  
            
        channel.close()
        connection.close()         
        print "END JOB"
        
        self._event.set()
        
