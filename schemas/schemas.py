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
    id: int
    task: str 

    class Config:
        orm_mode = True
  