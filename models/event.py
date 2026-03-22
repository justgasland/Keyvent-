from app import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, relationships, backref
import uuid
import datetime

class Event(Base):
    __tablename__= 'events'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    api_key_id = Column(String(36), ForeignKey('api_keys.id'), nullable=False)
    title= Column(String(200), nullable=False)
    description = Column(String(255), nullable=True)
    location    = Column(String(255), nullable=True)
    start_time  = Column(DateTime, nullable=False)
    end_time    = Column(DateTime, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow) 
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    rsvps       = Column(String(36), ForeignKey('rsvps.id'), nullable=True) 