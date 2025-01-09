from fastapi import HTTPException
from sqlalchemy.future import select
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import User, Todo
from schemas.schemas import TodoListDTO
from sqlalchemy.exc import SQLAlchemyError
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user_create, db: AsyncSession):
    result = await db.execute(select(User).filter(User.id == user_create.id))
    db_user = result.scalars().first()

    if db_user:
        return None 

    hashed_password = pwd_context.hash(user_create.password)
    new_user = User(id=user_create.id, password=hashed_password, name=user_create.name)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user_by_id(user_id: str, db: AsyncSession):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def add_todo_item(todo: TodoListDTO, db: AsyncSession) -> Todo:
    new_todo = Todo(task=todo.task)
    
    db.add(new_todo)
    await db.commit() 
    await db.refresh(new_todo) 
    
    return new_todo

async def get_all_todos_from_db(db: AsyncSession) -> List[Todo]:
    try:
        query = select(Todo)  
        result = await db.execute(query)  
        todos = result.scalars().all()  
        return todos
    except SQLAlchemyError as e:
        
        raise SQLAlchemyError(f"Database error: {str(e)}")

async def delete_todo_item(todo_id: int, db: AsyncSession):
    query = select(Todo).filter(Todo.id == todo_id)
    result = await db.execute(query)
    del_todo = result.scalar_one_or_none()

    if del_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    # 삭제 처리
    await db.delete(del_todo)  # 비동기식으로 삭제 처리
    await db.commit()  # 비동기 커밋

    return del_todo