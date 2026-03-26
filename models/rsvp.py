from app import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker, relationships, backref
import uuid
import datetime


class RSVP(Base):
    __tablename__ = 'rsvps'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey('events.id'), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    response = Column(String(20), nullable=False)  
    created_at = Column(DateTime, default=datetime.datetime.utcnow())
    updated_at = Column(DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
    __table_args__ = (UniqueConstraint('event_id', 'email'),)

   