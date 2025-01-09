from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from schemas.schemas import UserCreate, UserOut, LoginDTO, TodoListDTO
from crud.crud import create_user, get_user_by_id, verify_password, add_todo_item, delete_todo_item, get_all_todos_from_db
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import provide_session
from model.model import Todo
from typing import List

user_router = APIRouter()

@user_router.post("/users/sign_up", response_model=UserOut)
async def sign_up(user: UserCreate, db: AsyncSession = Depends(provide_session)):
    new_user = await create_user(user, db)

    if new_user is None:
        raise HTTPException(status_code=400, detail="User already exists.")

    return new_user

@user_router.post("/users/login")
async def login_user(form_data: LoginDTO, db: AsyncSession = Depends(provide_session)):
    db_user = await get_user_by_id(form_data.user_ID, db)

    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found.")

    if not await verify_password(form_data.user_PW, db_user.password):
        raise HTTPException(status_code=400, detail="Password mismatch.")

    return {"message": "Login successful", "user": {"id": db_user.id, "name": db_user.name}}


@user_router.post("/to_do_list/add")
async def todolist_add(add: TodoListDTO, db: AsyncSession = Depends(provide_session)):
    new_todo = await add_todo_item(add, db)
    return {"id": new_todo.id, "task": new_todo.task}


@user_router.get("/to_do_list/list", response_model=List[TodoListDTO])
async def get_all_todos(db: AsyncSession = Depends(provide_session)):
    try:
        todos = await get_all_todos_from_db(db)  
        if not todos:
            raise HTTPException(status_code=404, detail="No todos found")
        
        return todos
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@user_router.delete("/to_do_list/delete", response_model=TodoListDTO)
async def todolist_delete(todo_id: int, db: AsyncSession = Depends(provide_session)):
    # delete_todo_item 호출
    deleted_todo = await delete_todo_item(todo_id, db)
    return deleted_todo