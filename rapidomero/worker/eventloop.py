import pika
import yaml
import StringIO
import time
import jobhandler
import functools
import threading
import rapidomero.common.config as config

class AMQPLoop:
    
    # Create a channel variable to hold our channel object in
    __channel = None
    __event = threading.Event()
    __max_threads =5 
    __thread_list = []
    __path_to_config = None

    """
        Called when the connection to AMQP server is established. Then calls _on_channel_open
    """
    @classmethod
    def __on_connected(self, connection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        connection.channel(AMQPLoop.__on_channel_open)
    
    """
        Opens a channel for each queue in queue_config. Then calls _on_queue_declared
    """
    @classmethod
    def __on_channel_open(self, new_channel):
        """Called when our channel has opened"""
        AMQPLoop.__channel = new_channel
        """Add a queue for each element in config"""
        queue_configs = config.get_queue_configs(AMQPLoop.__path_to_config)
        for queue_config in queue_configs:
            print "Channel open for: "+queue_config["queue"]
            AMQPLoop.__channel.queue_declare(queue=queue_config["queue"], durable=True, exclusive=False, auto_delete=False, 
                                             callback=functools.partial(AMQPLoop.__on_queue_declared, queue_config=queue_config))

    """
        Calls ___handle_delivery when messages arrive
    """
    @classmethod
    def __on_queue_declared(self, frame, queue_config=None):
        print "Consume at: "+queue_config["queue"]
        AMQPLoop.__channel.basic_consume(functools.partial(AMQPLoop.__handle_delivery, queue_config=queue_config), 
                                         queue=queue_config["queue"])
    
    """
        Called when a message appears on the queue . Starts a job handler and checks
        There are not too many job handlers running at the same time.
    """
    @classmethod
    def __handle_delivery(self, channel, method, properties, body, queue_config):
        """Called when we receive a message from RabbitMQ"""
        stream = StringIO.StringIO(body)
        dictionary = yaml.load(stream)
        print str(dictionary)
        handler = jobhandler.Job_handler(queue_config, dictionary, properties.reply_to, AMQPLoop.__event)
        handler.start()
        AMQPLoop.__thread_list.append(handler)
        
        channel.basic_ack(delivery_tag = method.delivery_tag)
        
        #If the number of active threads is too high, wait for event
        #Race condition
        if (len(AMQPLoop.__thread_list)>AMQPLoop.__max_threads):
            AMQPLoop.__event.clear()
            AMQPLoop.__event.wait()
            
        for h in AMQPLoop.__thread_list:
            h.join(1)
            if h.isAlive() is False:
                AMQPLoop.__thread_list.remove(h)

    """
        Starts the event loop. 
        @param path_to_config: path to the config.yaml file
        @type path_to_config: string 
    """
    @classmethod
    def start(self, path_to_config):
        AMQPLoop.__path_to_config = path_to_config
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


