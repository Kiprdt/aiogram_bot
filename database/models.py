import datetime

import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, ForeignKey, Boolean, Text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Sequence
from sqlalchemy.engine import URL
import psycopg2
from sqlalchemy.orm import relationship, sessionmaker

db_url = '***'
engine = create_engine(db_url)

Base = sqlalchemy.orm.declarative_base()
Base.metadata.bind = engine

Session = sessionmaker(bind=engine)
session = Session()


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, nullable=False, primary_key=True)
    username = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    subscribe = Column(Boolean, nullable=False, default=False)
    black_list = Column(Boolean, nullable=False, default=False)



class UserWords(Base):
    __tablename__ = 'user_words'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    list_id = Column(Integer, default=Sequence('list_id'), nullable=False)
    indicator = Column(Boolean, nullable=False, default=False)
    word = Column(Text, nullable=False)
    translation = Column(Text, nullable=False)
    transcription = Column(Text, nullable=False)
    audio_data = Column(LargeBinary, nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    user = relationship("Users")


class Tasks(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    task = Column(Text, default=None)
    time = Column(String, default=None)
    day = Column(Integer, default=None)


Base.metadata.create_all(engine)
