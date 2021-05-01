from typing import List, Optional

from pydantic import BaseModel


class SocialAccountBase(BaseModel):
    name: str
    oauth_token: str
    oauth_token_secret: str


class SocialAccountCreate(SocialAccountBase):
    pass


class SocialAccount(SocialAccountBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str


class UserInDB(UserBase):
    password: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    status: bool

    # social_accounts: List[SocialAccount] = []

    # used to provide configurations to Pydantic
    # read the data even if it is not a dict
    class Config:
        orm_mode = True


class Logged_In_User(User):
    token: str
    token_type: str

    class Config:
        orm_mode = True


class Social_User(User):
    social_accounts: List[SocialAccount] = []
    # used to provide configurations to Pydantic
    # read the data even if it is not a dict
    class Config:
        orm_mode = True


class Url(BaseModel):
    url: str
