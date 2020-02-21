#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
@author: EFRI
"""

import time
import threading
import pika
from cgi import log


class MQTT(threading.Thread):

    def __init__(self, root, log):
        super().__init__()
        self.root = root
        self.log = log
        self._stop_event = threading.Event()
        self.channel=None
        self.connection = None
        self.url = 'amqp://gwvdueip:ZNzoi01UgQCttefdytXjUEDnzQYaHa6L@hawk.rmq.cloudamqp.com/gwvdueip'
        self.binding_key="topic_website"
        self.newexchange = 'topic_website'
        self.connect()
        
    def connect(self):
        params = pika.URLParameters(self.url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel() # start a channel
        self.channel.exchange_declare(exchange='topic_website', exchange_type='topic')

        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        if not self.binding_key:
           self.binding_key="#"
        self.channel.queue_bind(exchange=self.newexchange, queue=queue_name, routing_key=self.binding_key)
        self.channel.exchange_bind(destination=self.newexchange, source='amq.topic', routing_key='topic_website_route')
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for logs. To exit press CTRL+C')

    def run(self):
        while not self._stop_event.is_set():
            self.channel.start_consuming()

    def stop(self):
        self.stop = True
        self.channel.stop_consuming(consumer_tag=None)
        self._stop_event.set()


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))




if __name__ == '__main__':
    at = MQTT(None,None)
    at.start()
   