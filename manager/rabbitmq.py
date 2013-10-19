#!/usr/bin/env python
from flask import json
import pika
import sys, uuid, time
from datetime import datetime
from manager.models import Node, Blob
from manager.database import db_session
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

def emit_manager(txt):  #Manager sends messages to nodes
    #print exchange_name +"emit"
    manager_channel.basic_publish(exchange=manager_exchange,
                               routing_key='',
                               body=txt)
    print " [emit_manager] Sent %r \n" % (txt,)

def rec_update():  #Manager receives messages from Nodes
    result = update_channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    update_channel.queue_bind(exchange=update_exchange,
                              queue=queue_name)

    print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
        print " [rec_update] %r  \n" % (body,)
        handle_body(body)

    update_channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)

    update_channel.start_consuming()


def handle_body(body):
    body_dict = json.loads(body)
    if body_dict["type"] == "POST":
        add_blob(body_dict)
        emit_manager(body)
    elif body_dict["type"] == "PUT":
        update_blob(body_dict)
        emit_manager(body)
    elif body_dict["type"] == "DELETE":
        delete_blob(body_dict)
        emit_manager(body)
    elif body_dict["type"] == "SYNC":
        sync_blobs(body_dict)
    

def sync_blobs(body_dict):
    #print "syncing"
    #time.sleep(1)
    nodes=db_session.query(Node).order_by(Node.id)
    sync_node = db_session.query(Node).get(body_dict["node_id"])
    source_node = sync_node
    for node in nodes:
        if not node.id == source_node.id:
            source_node = node
            break

    if not source_node == sync_node:
        blobs=db_session.query(Blob).order_by(Blob.id)
        for b in blobs:
            data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                    "type":"POST",
                    "node_id":source_node.id,
                    "node_ip":source_node.ip,
                    "node_port":source_node.port, 
                    "file_id":b.id, 
                    "upload_date":str(b.upload_date),
                    "file_last_update":str(b.last_change),
                    "file_previous_update":str(b.second_last_change)}
            emit_manager(json.dumps(data))

def add_blob(body_dict):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b0 = datetime.strptime(body_dict["upload_date"], date_format)
    b1 = datetime.strptime(body_dict["file_last_update"], date_format)
    b2 = datetime.strptime(body_dict["file_previous_update"], date_format)
    b = Blob(b0, b1, b2)
    db_session.add(b)
    db_session.commit()
    b.id = body_dict["file_id"]
    b.upload_date = b0
    b.last_change = b1
    b.second_last_change = b2
    db_session.commit()

def update_blob(body_dict):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b0 = datetime.strptime(body_dict["upload_date"], date_format)
    b1 = datetime.strptime(body_dict["file_last_update"], date_format)
    b2 = datetime.strptime(body_dict["file_previous_update"], date_format)
    
    b=db_session.query(Blob).get(body_dict["file_id"])
    if b == None:
        b = Blob(b0, b1, b2)
        db_session.add(b)
        db_session.commit()
        b.id = body_dict["file_id"]
        b.upload_date = b0
        b.last_change = b1
        b.second_last_change = b2
        db_session.commit()
    else:
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        b.upload_date = b0
        b.last_change = b1
        b.second_last_change = b2
        db_session.commit()

def delete_blob(body_dict):
    b=db_session.query(Blob).get(body_dict["file_id"])
    if not b == None:
        db_session.delete(b)
        db_session.commit()