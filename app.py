# DATABASE SETUP

from sqlalchemy import Column, Integer, String, DateTime, foreignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, relationships, backref
from sqlalchemy.ext.declarative import declarative_base


# models import
from models.api_key import APIKey
from models.event import Event
from models.rsvp import RSVP

engine= create_engine('sqlite:///keyvent.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()
Base= declarative_base()

Base.metadata.create_all(bind=engine)