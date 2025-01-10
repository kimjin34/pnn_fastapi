from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    id: str
    password: str
    name: str

class UserOut(BaseModel):
    id: str
    password: str
    name: str

class LoginDTO(BaseModel):
    user_ID: str
    user_PW: str

class TodoListDTO(BaseModel):
    task: str 
    description: str = None  # 설명도 수정할 수 있도록
    completed: bool = False

   
  