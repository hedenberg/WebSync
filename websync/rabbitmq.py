#!/usr/bin/env python
from flask import json
from werkzeug import secure_filename
from datetime import datetime
import pika
import sys, urllib2, cgi
from websync.database import db_session
from websync.models import Blob

manager_exchange ="Manager" #app.port
manager_connection = pika.BlockingConnection(pika.ConnectionParameters(host='130.240.108.57'))
manager_channel = manager_connection.channel()
manager_channel.exchange_declare(exchange=manager_exchange,
                                 type='fanout')

update_exchange ="Update" #app.port
update_connection = pika.BlockingConnection(pika.ConnectionParameters(host='130.240.108.57'))
update_channel = update_connection.channel()
update_channel.exchange_declare(exchange=update_exchange,
                                type='fanout')

last_message_id = -1

def rec_manager(node_id): #Nodes receieves messages from Manager
    result = manager_channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    manager_channel.queue_bind(exchange=manager_exchange,
                               queue=queue_name)
    print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
        global last_message_id
        print " [rec_manager] %r \n" % (body,)
        body_dict = json.loads(body)
        if not (last_message_id == body_dict["message_id"]) and not (node_id == body_dict["node_id"]):
            last_message_id = body_dict["message_id"]
            if body_dict["type"] == "POST":
                add_blob(body_dict)
            elif body_dict["type"] == "PUT":
                update_blob(body_dict)
            elif body_dict["type"] == "DELETE":
                delete_blob(body_dict)
        else:
            # Repeated message or message derived from me
            print "json: node_ip", body_dict["node_ip"]
            

    manager_channel.basic_consume(callback,
                                  queue=queue_name,
                                  no_ack=True)
    request_sync()
    manager_channel.start_consuming()

def emit_update(txt):  #Nodes sends messages to Manager
    update_channel.basic_publish(exchange=update_exchange,
                                 routing_key='',
                                 body=txt)
    print " [update_emit] Sent %r \n " % (txt,)

def request_sync():
    data = {"message_id":(uuid.uuid4().int & (1<<63)-1), "type":"SYNC"}
    emit_update(json.dumps(data))

def add_blob(body_dict):
    response = urllib2.urlopen("http://%s:%d/blob/%d/download" % (body_dict["node_ip"], body_dict["node_port"], body_dict["file_id"]))
    _, params = cgi.parse_header(response.headers.get('Content-Disposition', ''))
    fn = params['filename']
    f_size = sys.getsizeof(response) 
    f_blob = response.read()
    b = Blob(fn,f_blob, f_size)
    db_session.add(b)
    db_session.commit()
    b.id = body_dict["file_id"]
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b.last_change = datetime.strptime(body_dict["file_last_update"], date_format)
    b.upload_date = datetime.strptime(body_dict["file_previous_update"], date_format)
    db_session.commit()

def update_blob(body_dict):
    response = urllib2.urlopen("http://%s:%d/blob/%d/download" % (body_dict["node_ip"], body_dict["node_port"], body_dict["file_id"]))
    _, params = cgi.parse_header(response.headers.get('Content-Disposition', ''))
    fn = params['filename']
    f_size = sys.getsizeof(response) 
    f_blob = response.read()
    
    b=db_session.query(Blob).get(body_dict["file_id"])
    if b == None:
        b = Blob(fn,f_blob, f_size)
        db_session.add(b)
        db_session.commit()
        b.id = body_dict["file_id"]
    else:
        b.lob = f_blob
        b.filesize = f_size
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b.last_change = datetime.strptime(body_dict["file_last_update"], date_format)
    b.upload_date = datetime.strptime(body_dict["file_previous_update"], date_format)
    db_session.commit()

def delete_blob(body_dict):
    b=db_session.query(Blob).get(body_dict["file_id"])
    if not b == None:
        db_session.delete(b)
        db_session.commit()