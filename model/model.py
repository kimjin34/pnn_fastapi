
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'login'

    id = Column(String, primary_key=True, index=True)
    password = Column(String, index=True)
    name = Column(String, index=True)