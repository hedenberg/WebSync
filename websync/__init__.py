from flask import Flask
app = Flask(__name__)
port = 1000
def setPort(newPort):
	global port
	print "NewPort:", newPort
	port = newPort
from websync.database import init_db
init_db()
import websync.views