#!/usr/bin/env python
from flask import json
import pika
import sys, urllib2
import websync.views
from websync.database import db_session

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
        print " [rec_manager] %r \n" % (body,)
        body_dict = json.loads(body)
        emit_update("test")
        if not views.node_id == body_dict["node_id"]:

            #http://130.240.111.132:8001/blob/1/download
            f = urllib2.urlopen("http://%s:%d/blob/%d/download" % body_dict["node_ip"], 
                                                                  body_dict["node_port"],
                                                                  body_dict["file_id"])
            #f = request.read()
            fn = secure_filename(f.filename)
            f_size = sys.getsizeof(f) 
            f_blob = f.read()
            b = Blob(fn,f_blob, f_size)
            db_session.add(b)
            db_session.commit()
            b.id = body_dict["file_id"]
            b.last_change = body_dict["file_last_update"]
            b.upload_date = body_dict["file_previous_update"]

    manager_channel.basic_consume(callback,
                                  queue=queue_name,
                                  no_ack=True)

    manager_channel.start_consuming()


##*********************** Nodes -> Manager ******************************


def emit_update(txt):  #Nodes sends messages to Manager
    update_channel.basic_publish(exchange=update_exchange,
                                 routing_key='',
                                 body=txt)
    print " [update_emit] Sent %r \n " % (txt,)