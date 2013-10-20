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
        self.upload_date = upload_date
        self.last_change = last_change
        self.second_last_change = second_last_change

    def __repr__(self):
        return '<ID %r>' % (self.id)

class VM(Base):
    __tablename__ = 'vm'
    id = Column(Integer, primary_key=True)
    ip = Column(String(50))
    instance = Column(String(50))

    def __init__(self, ip, instance):
        self.ip = ip
        self.instance = instance

    def __repr__(self):
        return '<ID %r>' % (self.id)

