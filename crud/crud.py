from fastapi import HTTPException
from sqlalchemy.future import select
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import User, Todo
from schemas.schemas import TodoListDTO
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import List, Dict

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict[str, str], expires_delta: timedelta = None) -> str:
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta  

    
    if expire < datetime.now(timezone.utc):
        raise ValueError("Expiration time cannot be in the past.")

    to_encode.update({"exp": expire})
    
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

 
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


async def add_todo_item(todo: TodoListDTO, db: AsyncSession, current_user: User) -> Todo:
    
    new_todo = Todo(task=todo.task, user_id=current_user.numder)
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    
    return new_todo


async def get_all_todos_from_db(db: AsyncSession, current_user: User) -> List[Todo]:
    try:
        query = select(Todo).filter(Todo.user_id == current_user.numder)  
        result = await db.execute(query)
        todos = result.scalars().all()
        return todos
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def update_todo_item(todo_id: int, todo_update: TodoListDTO, db: AsyncSession, user: User) -> Todo:
    
    todo = await db.execute(select(Todo).filter(Todo.id == todo_id))
    todo = todo.scalars().first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if todo.user_id != user.numder: 
        raise HTTPException(status_code=403, detail="You do not have permission to modify this todo.")

    todo.task = todo_update.task
    todo.description = todo_update.description
    todo.completed = todo_update.completed

    db.add(todo)
    await db.commit()
    await db.refresh(todo)  

    return todo

async def delete_todo_item(todo_id: int, db: AsyncSession):
    
    query = select(Todo).filter(Todo.id == todo_id)
    result = await db.execute(query)
    del_todo = result.scalar_one_or_none()
 
    if del_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    try:       
        await db.delete(del_todo)
        await db.commit()  
        
        return del_todo 
    except SQLAlchemyError as e:
        await db.rollback() 
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")