#!/usr/bin/env python
import pika
import sys
import websync.views

manager_exchange ="Manager" #app.port
manager_connection = pika.BlockingConnection(pika.ConnectionParameters(host='130.240.110.14'))
manager_channel = manager_connection.channel()
manager_channel.exchange_declare(exchange=manager_exchange,
                                 type='fanout')

update_exchange ="Update" #app.port
update_connection = pika.BlockingConnection(pika.ConnectionParameters(host='130.240.110.14'))
update_channel = update_connection.channel()
update_channel.exchange_declare(exchange=update_exchange,
                                type='fanout')


##***************** Manager -> Nodes *************************

def rec_manager(): #Nodes receieves messages from Manager
    result = manager_channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    manager_channel.queue_bind(exchange=manager_exchange,
                               queue=queue_name)
    print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
        print " [x] %r" % (body,)
        emit_update("Det fungerade")

    manager_channel.basic_consume(callback,
                                  queue=queue_name,
                                  no_ack=True)

    manager_channel.start_consuming()


##*********************** Nodes -> Manager ******************************


def emit_update(txt):  #Nodes sends messages to Manager
    update_channel.basic_publish(exchange=update_exchange,
                                 routing_key='',
                                 body=txt)
    print " [x] Sent %r" % (txt,)