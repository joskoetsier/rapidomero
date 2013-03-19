import rapidomero.worker.eventloop
import sys

argument = None
if len(sys.argv)==2:
    argument = sys.argv[1]
rapidomero.worker.eventloop.AMQPLoop.start(argument)
