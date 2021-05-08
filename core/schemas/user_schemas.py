from typing import List, Optional
from core.schemas import group_categories
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


class User(UserBase):
    id: Optional[int]
    is_active: Optional[bool]
    is_deleted: Optional[bool]

class UserCreate(User):
    password: str

    # social_accounts: List[SocialAccount] = []

    # used to provide configurations to Pydantic
    # read the data even if it is not a dict
    class Config:
        orm_mode = True


class Logged_In_User(BaseModel):
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

class User_Group_Categories(User):
    group_categories: List['group_categories.GroupCategory'] = []
    # used to provide configurations to Pydantic
    # read the data even if it is not a dict

    class Config:
        orm_mode = True


class Url(BaseModel):
    url: str
