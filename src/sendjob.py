import producer.send
import bliss.saga.job
import common.config

job = bliss.saga.job.Description()
job.parameters=["/home/jos"]
producer.send.send_job(common.config.get_queue_configs()[1], job)
