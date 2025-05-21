from pydantic import BaseModel
from datetime import datetime
from typing import Union

class TaskCreate(BaseModel):
    title: str
    description: Union[str, None] = None
    status: str = "в ожидании"
    priority: int = 1

class TaskInfo(BaseModel):
    id: int
    title: str
    description: Union[str, None]
    status: str
    creation_time: datetime
    priority: int
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str