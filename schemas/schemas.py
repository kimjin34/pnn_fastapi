from pydantic import BaseModel

class UserCreate(BaseModel):
    id: str
    password: str
    name: str

class UserOut(BaseModel):
    id: str
    password: str
    name: str