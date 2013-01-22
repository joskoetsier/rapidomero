import producer.send
import bliss.saga.job
import common.config


def callback(body):
    print body
    
    
job = bliss.saga.job.Description()
job.parameters=["/home/jos"]

sender = producer.send.sender(common.config.get_queue_configs()[0])
sender.send_job(job)
sender.consume_status(callback)
