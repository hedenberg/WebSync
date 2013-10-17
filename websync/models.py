from sqlalchemy import Column, Integer, String, DateTime, BLOB, BigInteger
from datetime import datetime
from websync.database import Base
import uuid

def randommeth():
    return (uuid.uuid4().int & (1<<63)-1)

# It's not a blob.. 
class Blob(Base):
    __tablename__ = 'blob'
    id = Column(Integer,primary_key=True,default=(randommeth))
    filename = Column(String(50))
    lob = Column(BLOB)
    file_size = Column(String(50))
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_change = Column(DateTime, default=datetime.utcnow)
    second_last_change = Column(DateTime, default=datetime.utcnow)

    def __init__(self, filename, lob, size):
        self.filename = filename
        self.lob = lob
        self.file_size = size

    def __repr__(self):
        return '<Filename %r>' % (self.filename)