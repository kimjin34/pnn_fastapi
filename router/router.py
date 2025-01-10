from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from schemas.schemas import UserCreate, UserOut, LoginDTO, TodoListDTO
from crud.crud import create_user, get_user_by_id, verify_password, add_todo_item, delete_todo_item, get_all_todos_from_db, verify_token, create_access_token, update_todo_item
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import provide_session
from model.model import Todo, User
from typing import List

user_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(provide_session)):
    payload = verify_token(token)  
    user_id = payload.get("sub") 
    user = await db.execute(select(User).filter(User.id == user_id))  
    user = user.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@user_router.post("/users/check_username")
async def check_username(user: UserCreate, db: AsyncSession = Depends(provide_session)):
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == user.id))
        db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "Username is available"}

@user_router.post("/users/sign_up", response_model=UserOut)
async def sign_up(user: UserCreate, db: AsyncSession = Depends(provide_session)):
    new_user = await create_user(user, db)

    if new_user is None:
        raise HTTPException(status_code=400, detail="User already exists.")

    return new_user

@user_router.post("/users/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(provide_session)):
    db_user = await get_user_by_id(form_data.username, db)

    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found.")

    if not await verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Password mismatch.")

    access_token = create_access_token(data={"sub": db_user.id})  
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post("/to_do_list/add")
async def todolist_add(add: TodoListDTO, db: AsyncSession = Depends(provide_session), current_user: User = Depends(get_current_user)):
    new_todo = await add_todo_item(add, db, current_user)
    return {"id": new_todo.id, "task": new_todo.task}


@user_router.get("/to_do_list/list")
async def get_all_todos(db: AsyncSession = Depends(provide_session), current_user: User = Depends(get_current_user)):
    try:
        todos = await get_all_todos_from_db(db, current_user)
        if not todos:
            raise HTTPException(status_code=404, detail="No todos found")
        return todos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@user_router.put("/to_do_list/update/{todo_id}")
async def update_todo(todo_id: int, todo_update: TodoListDTO, db: AsyncSession = Depends(provide_session), current_user: User = Depends(get_current_user)):
    # 특정 todo 항목을 수정
    updated_todo = await update_todo_item(todo_id, todo_update, db, current_user)
    
    # 수정된 todo 항목 반환
    return {"updated_todo": updated_todo}

@user_router.delete("/to_do_list/delete", response_model=TodoListDTO)
async def todolist_delete(task: int=Query(...), db: AsyncSession = Depends(provide_session)):
    
    deleted_todo = await delete_todo_item(task, db)
    return deleted_todo