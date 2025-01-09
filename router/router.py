from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas import UserCreate, UserOut
from crud.crud import create_user, get_user_by_id, verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import provide_session

user_router = APIRouter()

@user_router.post("/users/sign_up", response_model=UserOut)
async def sign_up(user: UserCreate, db: AsyncSession = Depends(provide_session)):
    new_user = await create_user(user, db)
    
    if new_user is None:
        raise HTTPException(status_code=400, detail="User already exists.")
    
    return new_user

@user_router.post("/users/login")
async def login_user(user_ID: str, user_PW: str, db: AsyncSession = Depends(provide_session)):
    db_user = await get_user_by_id(user_ID, db)
    
    if db_user is None:
        raise HTTPException(status_code=400, detail="User not found.")
    
    if not await verify_password(user_PW, db_user.password):
        raise HTTPException(status_code=400, detail="Password mismatch.")
    
    return {"message": "Login successful", "user": {"id": db_user.id, "name": db_user.name}}

#@user_oruter.
