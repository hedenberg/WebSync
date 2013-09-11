from flask import Flask
app = Flask(__name__)

from websync.database import init_db
init_db()
import websync.views