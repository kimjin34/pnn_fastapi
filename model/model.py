from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    numder = Column(Integer, primary_key=True, index=True)
    id= Column(String, unique=True, index=True)
    password = Column(String, index=True)
    name = Column(String, index=True)
    
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")


class Todo(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.numder')) 
    
    items = relationship("TodoItem", back_populates="todo", cascade="all, delete", passive_deletes=True)

    owner = relationship("User", back_populates="todos")


class TodoItem(Base):
    __tablename__ = 'todo_items'
    
    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey('todos.id', ondelete="CASCADE"))
    description = Column(String)
    
    todo = relationship("Todo", back_populates="items")
