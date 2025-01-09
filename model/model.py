
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)
    password = Column(String, index=True)
    name = Column(String, index=True)

Base = declarative_base()

class Todo(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    due_date = Column(DateTime)