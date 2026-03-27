
from flask import Flask


app=Flask(__name__)


# DATABASE SETUP

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, relationships, backref
from sqlalchemy.ext.declarative import declarative_base

Base= declarative_base()
engine= create_engine('sqlite:///keyvent.db')

# models import
from models.api_key import APIKey
from models.event import Event
from models.rsvp import RSVP


Base.metadata.create_all(bind=engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


# ROUTES SETUP
from routes.keys import keysBlueprint
from routes.events import events_bp


app.register_blueprint(events_bp, url_prefix='/api/v1')
app.register_blueprint(keysBlueprint, url_prefix='/api/v1')