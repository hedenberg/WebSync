from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from manager.database import Base

class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    ip = Column(String(50))
    port = Column(Integer)
    process_id = Column(String(50))
    create_date = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, default=datetime.utcnow)

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __repr__(self):
        return '<IP_Port %r>' % (self.post)

class Blob(Base):
    __tablename__ = 'blob'
    id = Column(Integer, primary_key=True)
    upload_date = Column(DateTime)
    last_change = Column(DateTime)
    second_last_change = Column(DateTime)

    def __init__(self, upload_date, last_change, second_last_change):
        upload_date = upload_date
        last_change = last_change
        second_last_change = second_last_change

    def __repr__(self):
        return '<ID %r>' % (self.id)


#'{"file_id": 4174621450990330058, "file_last_update": "2013-10-19 12:05:21.159666", "file_previous_update": "2013-10-19 12:05:21.159679", "message_id": 4204527344485405682, "node_id": 1, "node_ip": "130.240.108.57", "node_port": 8001, "type": "POST", "upload_date": "2013-10-19 12:05:21.159628"}' 
#'{"file_id": 4174621450990330058, "file_last_update": "None", "file_previous_update": "None",                                             "message_id": 3301323654902401341, "node_id": 1, "node_ip": "130.240.108.57", "node_port": 8001, "type": "POST", "upload_date": "None"}' 
