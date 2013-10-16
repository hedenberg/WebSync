#!/usr/bin/env python
import pika
import sys
from websync.views import update_receive

exchange_emit ="Manager" #app.port
connection_emit = pika.BlockingConnection(pika.ConnectionParameters(
            host='130.240.110.14'))
channel_emit = connection_emit.channel()
channel_emit.exchange_declare(exchange=exchange_emit,
                         type='fanout')

exchange_rec ="Update" #app.port
connection_rec = pika.BlockingConnection(pika.ConnectionParameters(
            host='130.240.110.14'))
channel_rec = connection_rec.channel()
channel_rec.exchange_declare(exchange=exchange_rec,
                         type='fanout')


##***************** Manager -> Nodes *************************

def manager_rec_logs(): #Nodes receieves messages from Manager
    result = channel_emit.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel_emit.queue_bind(exchange=exchange_emit,
                       queue=queue_name)

    print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
      print " [x] %r" % (body,)


    channel_emit.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)

    channel_emit.start_consuming()


##*********************** Nodes -> Manager ******************************


def update_emit_log(txt):  #Nodes sends messages to Manager
    #print exchange_name +"emit"
    channel_rec.basic_publish(exchange=exchange_rec,
                          routing_key='',
                          body=txt)
    print " [x] Sent %r" % (txt,)