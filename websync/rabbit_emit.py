import pika
import sys
from websync import app

exchange_name ='nodeport'+app.port
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='130.240.110.14'))

channel = connection.channel()
<<<<<<< HEAD:websync/rabbitmq.py
channel.exchange_declare(exchange=exchange_name,
                         type='fanout')
=======

def init_emit_transfer(log_name):
    global exchange_name
    exchange_name=log_name.strip()
    #print exchange_name +"init"

    channel.exchange_declare(exchange=exchange_name,
                                 type='fanout')

>>>>>>> 838b3da21b7d85f56fa9cbc4e8ee774194ab6ef5:websync/rabbit_emit.py

def emit_log(txt):
    #print exchange_name +"emit"
    channel.basic_publish(exchange=exchange_name,
                          routing_key='',
                          body=txt)
    print " [x] Sent %r" % (txt,)
    

