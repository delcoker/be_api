from typing import List, Optional

from pydantic import BaseModel

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str


class User(UserBase):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    status: bool

    class Config:
        orm_mode = True
