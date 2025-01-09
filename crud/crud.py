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
    # 기본 만료 시간을 설정
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 데이터 복사 및 만료 시간 추가
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta  # UTC 기준으로 시간을 계산

    # 만약 만료 시간이 과거라면, 예외 처리 추가
    if expire < datetime.now(timezone.utc):
        raise ValueError("Expiration time cannot be in the past.")

    to_encode.update({"exp": expire})
    
    # JWT 인코딩
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 토큰의 만료 시간 체크
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    except Exception as e:
        # 예외에 대한 구체적인 오류 처리
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
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
    # 현재 로그인한 유저의 ID로 Todo 생성
    new_todo = Todo(task=todo.task, user_id=current_user.id)
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    
    return new_todo

async def get_all_todos_from_db(db: AsyncSession, current_user: User) -> List[Todo]:
    try:
        query = select(Todo).filter(Todo.user_id == current_user.id)  # 현재 유저의 Todo만 조회
        result = await db.execute(query)
        todos = result.scalars().all()
        return todos
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def delete_todo_item(todo_id: int, db: AsyncSession):
    # Todo 항목 찾기
    query = select(Todo).filter(Todo.id == todo_id)
    result = await db.execute(query)
    del_todo = result.scalar_one_or_none()

    # Todo가 존재하지 않으면 404 오류 발생
    if del_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    try:
        # Todo 삭제 (관련된 TodoItem도 자동 삭제됨)
        await db.delete(del_todo)
        await db.commit()  # 삭제된 내용 커밋
        
        return del_todo  # 삭제된 Todo 객체 반환
    except SQLAlchemyError as e:
        await db.rollback()  # 예외 발생 시 롤백
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")