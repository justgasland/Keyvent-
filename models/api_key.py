
import datetime
from app import Base
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, relationships, backref
import uuid


class APIKey(Base):
    __tablename__ = 'api_keys'
    id =Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key=Column(String(64), unique=True, nullable=False)
    name=Column(String(100), nullable=False)
    is_active=Column(Boolean, default=True, nullable=False)
    usage_count=Column(Integer, default=0, nullable=False)
    rate_limit=Column(Integer, default=200, nullable=False)
    request_this_hour=Column(Integer, default=0, nullable=False)
    window_start=Column(DateTime, nullable=True)
    last_used_at=Column(DateTime, nullable=True)
    created_at=Column(DateTime, default=datetime.datetime.utcnow())
    events=relationship('Event', backref='api_key', lazy=True)
