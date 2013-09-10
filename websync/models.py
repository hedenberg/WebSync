from sqlalchemy import Column, Integer, String
from websync.database import Base

# It's not a blob.. 
class Blob(Base):
    __tablename__ = 'blob'
    id = Column(Integer, primary_key=True)
    filename = Column(String(50), unique=True)

    def __init__(self, filename=None):
        self.filename = filename

    def __repr__(self):
        return '<Filename %r>' % (self.filename)