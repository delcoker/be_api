from typing import List, Optional

from pydantic import BaseModel




class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str

class UserInDB(User):
    hashed_password: str

class UserCreate(UserBase):
    # first_name: str
    # last_name: str
    # email: str
    # phone: str
    password: str
    # status: bool


class User(UserBase):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    status: bool

    class Config:
        orm_mode = True
