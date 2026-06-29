from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    counter = Column(Integer, default=0)
    last_visit = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(String, nullable=True)