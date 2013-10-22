#!/usr/bin/env python
from flask import json
from werkzeug import secure_filename
from datetime import datetime
import pika
import sys, urllib2, cgi, uuid
from websync.database import db_session
from websync.models import Blob

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

last_message_id = -1
online = True
node_id = 0

def set_online(bool):
    global online
    online=bool

def rec_manager(node_id_): #Nodes receieves messages from Manager
    global node_id
    node_id = node_id_
    result = manager_channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    manager_channel.queue_bind(exchange=manager_exchange,
                             queue=queue_name)
    print ' [*] Waiting for logs. To exit press CTRL+C'
    def callback(ch, method, properties, body):
        global online
        if online:
            global last_message_id
            print " [rec_manager] %r \n" % (body,)
            body_dict = json.loads(body)
            if not (last_message_id == body_dict["message_id"]):
                if body_dict["type"] == "CONFLICT":
                    if (node_id == body_dict["node_id"]):
                        handle_conflict(body_dict)
                if (node_id == body_dict["node_id"]):
                    last_message_id = body_dict["message_id"]
                    #These are returned after this node made an update
                    if body_dict["type"] == "POST":
                        add_update_succeed(body_dict)
                    elif body_dict["type"] == "PUT":
                        add_update_succeed(body_dict)
                    elif body_dict["type"] == "DELETE":
                        pass
                    elif body_dict["type"] == "STATUS":
                        pass
                    elif body_dict["type"] == "CONFLICT":
                        handle_conflict()
                    elif body_dict["type"] == "REUPLOAD":
                        reupload(body_dict)
                else:
                    last_message_id = body_dict["message_id"]
                    if body_dict["type"] == "POST":
                        add_update_blob(body_dict)
                    elif body_dict["type"] == "PUT":
                        add_update_blob(body_dict)
                    elif body_dict["type"] == "DELETE":
                        delete_blob(body_dict)
                    elif body_dict["type"] == "STATUS":
                        status(body_dict)
            else:
                # Repeated message or message derived from me
                print "json: node_ip", body_dict["node_ip"]
       
    manager_channel.basic_consume(callback,
                                  queue=queue_name,
                                  no_ack=True)
    manager_channel.start_consuming()

def emit_update(txt):  #Nodes sends messages to Manager
    update_channel.basic_publish(exchange=update_exchange,
                                 routing_key='',
                                 body=txt)
    print " [update_emit] Sent %r \n " % (txt,)

def request_sync(node_id, node_ip, node_port):
    print "requesting sync"
    blobs=db_session.query(Blob).order_by(Blob.id)
    blob_array = []
    for blob in blobs:
        blob_array.append((blob.id, str(blob.last_change), str(blob.last_sync)))
    data = {"message_id":(uuid.uuid4().int & (1<<63)-1), 
            "type":"SYNC",
            "node_id":node_id,
            "node_ip":node_ip,
            "node_port":node_port, 
            "blobs":blob_array}
    emit_update(json.dumps(data))

def reupload(body_dict):
    b = db_session.query(Blob).get(body_dict["file_id"])
    data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
            "type":"POST",
            "node_id":node_id,
            "node_ip":node_ip,
            "node_port":node_port, 
            "file_id":b.id, 
            "upload_date":str(b.upload_date),
            "file_last_update":str(b.last_change)}

def handle_conflict(body_dict):
    # Adding a new file
    old_blob = db_session.query(Blob).get(body_dict["file_id"])
    old_filename=old_blob.filename.split(".")
    new_filename = ""
    try:
        new_filename=old_filename[0]+"_conflict"+"."+old_filename[1]
    except IndexError:
        new_filename=old_filename[0]+"_conflict"
    new_blob = Blob(new_filename, old_blob.lob, old_blob.file_size)
    db_session.add(new_blob)
    db_session.delete(old_blob)
    db_session.commit()

    data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
            "type":"POST",
            "node_id":node_id,
            "node_ip":node_ip,
            "node_port":node_port, 
            "file_id":new_blob.id, 
            "upload_date":str(new_blob.upload_date),
            "file_last_update":str(new_blob.last_change)}

def add_update_blob(body_dict):
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
    b.last_sync = datetime.strptime(body_dict["file_last_sync"], date_format)
    db_session.commit()

def add_update_succeed(body_dict):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b=db_session.query(Blob).get(body_dict["file_id"])
    b.last_sync = datetime.strptime(body_dict["file_last_sync"], date_format)
    db_session.commit()

def delete_blob(body_dict):
    b=db_session.query(Blob).get(body_dict["file_id"])
    if not b == None:
        db_session.delete(b)
        db_session.commit()

def status(body_dict):
    blobs=db_session.query(Blob).order_by(Blob.id)
    blob_array = []
    for blob in blobs:
        blob_array.append((blob.id, str(blob.last_change), str(blob.last_sync)))
    data = {"message_id":(uuid.uuid4().int & (1<<63)-1), 
            "type":"STATUS",
            "node_id":node_id,
            "blobs":blob_array}
    emit_update(json.dumps(data))