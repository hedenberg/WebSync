from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from manager.database import Base

class Node(Base):
    __tablename__ = 'blob'
    id = Column(Integer, primary_key=True)
    ip = Column(String(50))
    port = Column(String(50))
    process_id = Column(String(50))
    create_date = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime, default=datetime.utcnow)

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __repr__(self):
        return '<IP_Port %r>' % (self.post)