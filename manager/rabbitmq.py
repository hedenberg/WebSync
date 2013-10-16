#!/usr/bin/env python
import pika
import sys
#from manager.views import manager_receive

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



def emit_manager(txt):  #Manager sends messages to nodes
    #print exchange_name +"emit"
    manager_channel.basic_publish(exchange=manager_exchange,
                               routing_key='',
                               body=txt)
    print " [emit_manager] Sent %r" % (txt,)


##*********************** Nodes -> Manager ******************************

def rec_update():  #Manager receives messages from Nodes
    result = update_channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    update_channel.queue_bind(exchange=update_exchange,
                              queue=queue_name)

    #print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
        #manager_receive(body)
        emit_manager(body)
        print " [rec_update] %r" % (body,)

    update_channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)

    update_channel.start_consuming()



