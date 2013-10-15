#!/usr/bin/env python
import pika
import sys

exchange_name ='None'
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='130.240.110.14'))

channel = connection.channel()

def init_transfer(log_name):
    global exchange_name
    exchange_name=log_name.strip()
    print exchange_name +"init"

    channel.exchange_declare(exchange=exchange_name,
                                 type='fanout')


def emit_log(txt):
    print exchange_name +"emit"
    channel.basic_publish(exchange=exchange_name,
                          routing_key='',
                          body=txt)
    print " [x] Sent %r" % (txt,)
    

