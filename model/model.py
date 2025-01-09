from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# User 모델
class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, index=True)  # id는 String 타입으로 설정
    password = Column(String, index=True)
    name = Column(String, index=True)

    # User와 Todo 간의 일대다 관계 설정
    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")

# Todo 모델
class Todo(Base):
    __tablename__ = 'todos'
    
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, index=True)
    user_id = Column(String, ForeignKey('users.id'))  # user_id는 외래키로 추가

    # Todo와 TodoItem 간의 일대다 관계 설정
    items = relationship("TodoItem", back_populates="todo", cascade="all, delete", passive_deletes=True)
    
    # Todo와 User 간의 관계 설정
    owner = relationship("User", back_populates="todos")

# TodoItem 모델
class TodoItem(Base):
    __tablename__ = 'todo_items'
    
    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey('todos.id', ondelete="CASCADE"))
    description = Column(String)
    
    # TodoItem과 Todo 간의 관계 설정
    todo = relationship("Todo", back_populates="items")
