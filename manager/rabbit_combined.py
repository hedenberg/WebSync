#!/usr/bin/env python
import pika
import sys
from manager.views import manager_receive

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



def manager_emit_log(txt):  #Manager sends messages to nodes
    #print exchange_name +"emit"
    channel_emit.basic_publish(exchange=exchange_emit,
                          routing_key='',
                          body=txt)
    print " [x] Sent %r" % (txt,)


##*********************** Nodes -> Manager ******************************

def update_rec_logs():  #Manager receives messages from Nodes
    result = channel_rec.queue_declare(exclusive=True)
    queue_name = result.method.queue

    channel_rec.queue_bind(exchange=exchange_rec,
                       queue=queue_name)

    #print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
      manager_receive(body)
      #print " [x] %r" % (body,)


    channel_rec.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)

    channel_rec.start_consuming()



