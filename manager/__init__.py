from flask import Flask
app = Flask(__name__)

from manager.database import init_db
init_db()
import manager.views