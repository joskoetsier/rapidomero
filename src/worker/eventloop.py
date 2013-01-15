import pika
import yaml
import StringIO
import time
import jobhandler
from common.constants import Constants

class AMQPLoop:
    
    # Create a channel variable to hold our channel object in
    __channel = None
    
    # Step #2
    @classmethod
    def __on_connected(self, connection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        connection.channel(AMQPLoop.__on_channel_open)
    
    # Step #3
    @classmethod
    def __on_channel_open(self, new_channel):
        """Called when our channel has opened"""
        AMQPLoop.__channel = new_channel
        AMQPLoop.__channel.queue_declare(queue=Constants.job_queue, durable=True, exclusive=False, auto_delete=False, callback=AMQPLoop.__on_queue_declared)

    # Step #4
    @classmethod
    def __on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
        AMQPLoop.__channel.basic_consume(AMQPLoop.__handle_delivery, queue=Constants.job_queue)
    
    # Step #5
    @classmethod
    def __handle_delivery(self, channel, method, header, body):
        """Called when we receive a message from RabbitMQ"""
        stream = StringIO.StringIO(body)
        dictionary = yaml.load(stream)
        handler = jobhandler.Job_handler(dictionary)
        handler.start()
        channel.basic_ack(delivery_tag = method.delivery_tag)
        
    @classmethod
    def start(self, ):
        parameters = pika.ConnectionParameters()
        connection = pika.SelectConnection(parameters, AMQPLoop.__on_connected)
        
        try:
            # Loop so we can communicate with RabbitMQ
            connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            connection.close()
            # Loop until we're fully closed, will stop on its own
            connection.ioloop.start()


