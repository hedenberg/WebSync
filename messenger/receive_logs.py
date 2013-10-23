#!/usr/bin/env python
import pika, sys

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='130.240.233.94'))
channel = connection.channel()

exchange_name=sys.argv[1]

channel.exchange_declare(exchange=exchange_name,
                         type='fanout')

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