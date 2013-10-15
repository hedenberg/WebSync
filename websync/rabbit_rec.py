#!/usr/bin/env python
import pika
import sys

exchange_name ='nodeport'+app.port
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='130.240.110.14'))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name,
                         type='fanout')


def rec_logs():
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=exchange_name,
                       queue=queue_name)

    print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
      print " [x] %r" % (body,)

    channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)

    channel.start_consuming()





