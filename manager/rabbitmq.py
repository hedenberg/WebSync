#!/usr/bin/env python
from flask import json
import pika
import sys, uuid, time
from datetime import datetime
from manager.models import Node, Blob
from manager.database import db_session
from manager import node_status as ns 
#from manager.views import manager_receive

manager_exchange ="Manager" #app.port #130.240.110.14
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
    elif body_dict["type"] == "PUT":
        update_blob(body_dict)
    elif body_dict["type"] == "DELETE":
        delete_blob(body_dict)
        emit_manager(body)
    elif body_dict["type"] == "SYNC":
        sync_blobs(body_dict)
    elif body_dict["type"] == "STATUS":
        status(body_dict)

""" 
def status(body_dict):
    node=db_session.query(Node).get(body_dict["node_id"])
    blobs = body_dict["blobs"]
    status = 0
    #Check that manager has all files node has
        #Check dates

    for blob_node in blobs:
        blob_id, blob_last, blob_second = blob_node
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        bl_node = datetime.strptime(blob_last, date_format)
        bs_node = datetime.strptime(blob_second, date_format)
        blob_manager=db_session.query(Blob).get(blob_id)
        if blob_manager == None:
            # Manager does not have 
            status = ns.NODE_STATUS_NEW_FILE
            break
        if not bl_node == blob_manager.last_change:
            # Time not same 
            status = ns.NODE_STATUS_UPDATED_FILE
            break

    #Check that node has all files that manager has
    blobs_manager = db_session.query(Blob).order_by(Blob.id)
    for blob_manager in blobs_manager:
        found = False
        for blob_node in blobs:
            blob_id, blob_last, blob_second = blob_node
            
            if blob_id == blob_manager.id:
                found = True
                break
        if not found:
            status = ns.NODE_STATUS_MISSING_FILE
            break

    if status == 0:
        print "Status is awesome, Status: ", status
    else:
        print "Damn yuuh, Status: ", status

    node.status = status
    db_session.commit()
"""

def sync_blobs(body_dict):
    
    nodes=db_session.query(Node).order_by(Node.id)
    sync_node = db_session.query(Node).get(body_dict["node_id"])
    source_node = sync_node
    for node in nodes:
        if not node.id == source_node.id:
            source_node = node
            break

    #if not source_node == sync_node:
    blobs_manager=db_session.query(Blob).order_by(Blob.id)
    for blob_manager in blobs_manager:
        blobs_node=body_dict["blobs"]
        blob_node=None
        for b in blobs_node:
            b_id, b_last_change, b_last_sync = b
            if b_id == blob_manager.id:
                blob_node=b
                break
        if not blob_node == None:
            blob_id, blob_last_change, blob_last_sync = blob_node
            if not (blob_last_sync == str(blob_manager.last_sync)):
                #Update has changed on cloud when node was offline
                if not (blob_last_change == blob_last_sync):
                    #AMAGAAAD CONFLICT
                    print "Manager and node has file, conflict detected"
                    data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                            "type":"CONFLICT",
                            "node_id":sync_node.id,
                            "file_id":blob_id}
                    emit_manager(json.dumps(data))
                print "Pushing manager-version to all nodes"
                data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                    "type":"POST",
                    "node_id":source_node.id,
                    "node_ip":source_node.ip,
                    "node_port":source_node.port, 
                    "file_id":blob_manager.id, 
                    "upload_date":str(blob_manager.upload_date),
                    "file_last_update":str(blob_manager.last_change),
                    "file_last_sync":str(blob_manager.last_sync)}
                emit_manager(json.dumps(data))
            else:
                if not (blob_last_change== str(blob_manager.last_change)):
                    #This node has changed file when offline.
                    date_format = '%Y-%m-%d %H:%M:%S.%f'
                    blob_manager.last_change =  datetime.strptime(blob_last_change, date_format)
                    blob_manager.last_sync = blob_manager.last_change
                    db_session.commit()
                    print "Node changed file but hadn't synced it. Manager tells everyone to pull from node"
                    data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                            "type":"PUT",
                            "node_id":sync_node.id,
                            "node_ip":sync_node.ip,
                            "node_port":sync_node.port, 
                            "file_id":blob_manager.id, 
                            "upload_date":str(blob_manager.upload_date),
                            "file_last_update":str(blob_manager.last_change),
                            "file_last_sync":str(blob_manager.last_sync)}
                    emit_manager(json.dumps(data))
        else:
            print "Node does not have file, tells node to get it from a source-node"
            data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                    "type":"POST",
                    "node_id":source_node.id,
                    "node_ip":source_node.ip,
                    "node_port":source_node.port, 
                    "file_id":blob_manager.id, 
                    "upload_date":str(blob_manager.upload_date),
                    "file_last_update":str(blob_manager.last_change),
                    "file_last_sync":str(blob_manager.last_sync)}
            emit_manager(json.dumps(data))
    #else:
    blobs_node=body_dict["blobs"]
    blobs_manager=db_session.query(Blob).order_by(Blob.id)
    for blob_node in blobs_node:
            blob_node_id, blob_node_last_change, blob_node_last_sync = blob_node
            blob_manager = None
            for b in blobs_manager:
                if b.id == blob_node_id:
                    blob_manager=b
                    break
            if not blob_manager == None:
                if not (blob_node_last_sync == str(blob_manager.last_sync)):
                    #Update has changed on cloud when node was offline
                    if not (blob_node_last_change == blob_node_last_sync):
                        #AMAGAAAD CONFLICT
                        print "Conflict found in second for-loop.. weird"
                        data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                                "type":"CONFLICT",
                                "node_id":sync_node.id,
                                "file_id":blob_node_id}
                        emit_manager(json.dumps(data))
                    print "Second loop.. sending file to node"
                    data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                        "type":"POST",
                        "node_id":source_node.id,
                        "node_ip":source_node.ip,
                        "node_port":source_node.port, 
                        "file_id":blob_manager.id, 
                        "upload_date":str(blob_manager.upload_date),
                        "file_last_update":str(blob_manager.last_change),
                        "file_last_sync":str(blob_manager.last_sync)}
                    emit_manager(json.dumps(data))
                else:
                    if not (blob_node_last_change== str(blob_manager.last_change)):
                        #This node has changed file when offline.
                        date_format = '%Y-%m-%d %H:%M:%S.%f'
                        blob_manager.last_change =  datetime.strptime(blob_node_last_change, date_format)
                        blob_manager.last_sync = blob_manager.last_change
                        db_session.commit()
                        print "Node has changed file. Tells all other nodes to pull from it"
                        data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                                "type":"PUT",
                                "node_id":sync_node.id,
                                "node_ip":sync_node.ip,
                                "node_port":sync_node.port, 
                                "file_id":blob_manager.id, 
                                "upload_date":str(blob_manager.upload_date),
                                "file_last_update":str(blob_manager.last_change),
                                "file_last_sync":str(blob_manager.last_sync)}
                        emit_manager(json.dumps(data))
            else:
                print "Node has added file when offline, asks it to push it again"
                data = {"message_id":(uuid.uuid4().int & (1<<63)-1),
                        "type":"REUPLOAD",
                        "node_id":sync_node.id,
                        "file_id":blob_node_id}
                emit_manager(json.dumps(data))






def add_blob(body_dict):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b0 = datetime.strptime(body_dict["upload_date"], date_format)
    b1 = datetime.strptime(body_dict["file_last_update"], date_format)
    b=db_session.query(Blob).get(body_dict["file_id"])
    if b == None:
        print "Blob did not exist"
        b = Blob(b0, b1, b1)
        db_session.add(b)
        db_session.commit()
    b.id = body_dict["file_id"]
    b.upload_date = b0
    b.last_change = b1
    b.last_sync = b1
    db_session.commit()
    print "add_blob"
    bs=db_session.query(Blob).order_by(Blob.id)
    for b_ in bs:
        print "blob: ",b_.id
    data = {"message_id":body_dict["message_id"],
            "type":body_dict["type"],
            "node_id":body_dict["node_id"],
            "node_ip":body_dict["node_ip"],
            "node_port":body_dict["node_port"], 
            "file_id":body_dict["file_id"], 
            "upload_date":body_dict["upload_date"],
            "file_last_update":body_dict["file_last_update"],
            "file_last_sync":str(b1)}
    emit_manager(json.dumps(data))

def update_blob(body_dict):
    date_format = '%Y-%m-%d %H:%M:%S.%f'
    b0 = datetime.strptime(body_dict["upload_date"], date_format)
    b1 = datetime.strptime(body_dict["file_last_update"], date_format)
    b2 = datetime.utcnow()
    
    b=db_session.query(Blob).get(body_dict["file_id"])
    if b == None:
        b = Blob(b0, b1, b2)
        db_session.add(b)
        db_session.commit()
        b.id = body_dict["file_id"]
        b.upload_date = b0
        b.last_change = b1
        b.last_sync = b2
        db_session.commit()
    else:
        date_format = '%Y-%m-%d %H:%M:%S.%f'
        b.upload_date = b0
        b.last_change = b1
        b.second_last_change = b2
        db_session.commit()
    data = {"message_id":body_dict["message_id"],
            "type":body_dict["type"],
            "node_id":body_dict["node_id"],
            "node_ip":body_dict["node_ip"],
            "node_port":body_dict["node_port"], 
            "file_id":body_dict["file_id"], 
            "upload_date":body_dict["upload_date"],
            "file_last_update":body_dict["file_last_update"],
            "file_last_sync":str(b2)}
    emit_manager(json.dumps(data))

def delete_blob(body_dict):
    b=db_session.query(Blob).get(body_dict["file_id"])
    if not b == None:
        db_session.delete(b)
        db_session.commit()