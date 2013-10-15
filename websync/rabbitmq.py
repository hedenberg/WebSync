import pika
import sys
from websync import app

exchange_name ='nodeport'+app.port
connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='130.240.110.14'))

channel = connection.channel()
channel.exchange_declare(exchange=exchange_name,
                         type='fanout')

def emit_log(txt):
    print exchange_name +"emit"
    channel.basic_publish(exchange=exchange_name,
                          routing_key='',
                          body=txt)
    print " [x] Sent %r" % (txt,)
    

