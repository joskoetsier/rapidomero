import pika
import time
import yaml
import rapidomero.common.utils
import saga
from threading import Thread
import logging
import rapidomero.streaming.context
import rapidomero.streaming.operations

class Job_handler(Thread):
    
    """
        Constructs job handler
        @param queue_config: configuration of the queue
        @type queue_config: dict
        @param reply_to: queue name to reply messages to
        @type reply_to: string
        @param event: Used to ensure not too many threads run at once.
        @type event: threading.Event
    """
    def __init__(self, queue_config, variables, reply_to, event):
        super(Job_handler, self).__init__()
        self._queue_config = common.utils.resolve(queue_config, variables)
        self._reply_to = reply_to
        self._event = event
        self._queue_name = self._queue_config.get("queue")
        self._queue_host = self._queue_config.get("host")
        self._job = self._queue_config.get("job")
        self._service = self._queue_config.get("service")
        self._files = self._queue_config.get("files")
                
        logging.log(logging.DEBUG, queue_config)
                
    """
        Runs the job. 
    """
    def run(self):
        if self._job is not None and self._service is not None:
            self.do_job()
        if self._files is not None:
            for f in self._files:
                self.do_file(f) 

    """
        The job is a file transfer job. 
        @type file_element: dictionary
        @param file_element: file transfer portion of the config.yaml file
    """
    def do_file(self, file_element):
        source = file_element.get("source")
        target = file_element.get("target")
        
        def buildctx(transfer):
            userid  = transfer.get("userid") # your identity on the remote machine
            key_filename = transfer.get("userkey") # ssh key to use (only necessary if in non-default location)
            password = transfer.get("password") #password to use
            return streaming.context.context(username=userid, key_filename=key_filename, password=password)
        
        sourcectx = buildctx(source)
        targetctx = buildctx(target)

        #create the reply_to queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(self._queue_host))
        channel = connection.channel()

        reply = dict() 
        reply["message"] = None
        reply["status"] =  str(saga.job.Job.Running)
        reply["jobid"] = "0" 
        
        message = yaml.dump(reply)  
        channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)  
        try:
            streaming.operations.copy_urls(source.get("url"), target.get("url"),  sourcectx, targetctx)   
            reply["status"] =  str(saga.job.Job.Done)
        except Exception, e:
            reply["status"] =  str(saga.job.Job.Failed)
            reply["message"] = "'"+str(e)+"'"
        
        message = yaml.dump(reply)  
        channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)  
       
        channel.close()
        connection.close()      
        
        self._event.set() 
        
    """
        Its a computational job.
    """
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
        ctx = saga.Context(type='ssh')
        if (connection_method.lower()=="ssh" or connection_method.lower()=="gsissh"):
            ctx.type = 'ssh'
            ctx.user_id  = self._service["userid"] # your identity on the remote machine
            ctx.user_key = self._service["userkey"] # ssh key to use (only necessary if in non-default location)
            ctx.user_cert = self._service["usercert"] # ssh key to use (only necessary if in non-default location)
        
        ses = saga.Session()
        ses.contexts.append(ctx)
        
        #create job 
        jobstate = None
        reply = dict()    
        js = saga.job.Service(url,session=ses) 
        thejob = js.create_job(common.utils.dict_to_description(self._job))
        try:          
            js = saga.job.Service(url,session=ses)
            thejob = js.create_job(common.utils.dict_to_description(self._job))
            thejob.run()
            print "Started Job: "
            print self._job
            jobstate = thejob.get_state()
            reply["message"] = None
            reply["status"] =  str(jobstate)
        except saga.SagaException as ex:
            print "Exception thrown"
            print str(ex)
            reply["message"] = ex.message
            reply["status"] = str(saga.job.FAILED)    
        finally:
            reply["jobid"] = str(thejob.id)
            
        #create the reply_to queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(self._queue_host))
        channel = connection.channel()
        #passive=False, durable=False, exclusive=False, auto_delete=False, nowait=False, arguments=None
        #channel.queue_declare(queue=self._reply_to, durable=False, exclusive=False, auto_delete=True)
        #thejob.wait(-1)  
        #send the state as soon as it has changed. Poll
        polling_time = float(self._service["pollingtime"])
        
        message = yaml.dump(reply)
        channel.basic_publish(exchange='', routing_key=self._reply_to, body=message)
         
        newjobstate = jobstate    
        print str(jobstate)          
        while jobstate is not saga.job.DONE and jobstate is not saga.job.FAILED:                    
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
        
        self._event.set()
        
