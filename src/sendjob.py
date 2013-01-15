import producer.send
import bliss.saga.job

job = bliss.saga.job.Description()
job.executable="/bin/ls"
job.parameters=["/home/jos"]
job.output="/tmp/out.txt"
producer.send.send_job(job)
