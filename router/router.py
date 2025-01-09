from fastapi import APIRouter, Depends, Form, HTTPException
from schemas.schemas import UserCreate, UserOut, LoginDTO, TodoListDTO
from crud.crud import create_user, get_user_by_id, verify_password, add_todo_item
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import provide_session

user_router = APIRouter()

@user_router.post("/users/sign_up", response_model=UserOut)
async def sign_up(user: UserCreate, db: AsyncSession = Depends(provide_session)):
    new_user = await create_user(user, db)

    if new_user is None:
        raise HTTPException(status_code=400, detail="User already exists.")

    return new_user



user_router = APIRouter()

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
    return {"id": new_todo.id, "task": new_todo.task, "due_date": new_todo.due_date}