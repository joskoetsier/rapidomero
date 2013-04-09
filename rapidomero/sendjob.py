import rapidomero.producer.send
import rapidomero.common.config

def callback(body):
    print body

sender = producer.send.sender("condor")
variables = {"name" : "pip-0.7.2"}
jobid = sender.send_job(variables)
sender.consume_status(jobid, callback)
