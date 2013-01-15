import producer.send
import bliss.saga.job

job = bliss.saga.job.Description()
job.parameters=["/home/jos"]
producer.send.send_job(job)
