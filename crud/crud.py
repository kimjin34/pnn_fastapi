from sqlalchemy.future import select
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from model.model import User

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
