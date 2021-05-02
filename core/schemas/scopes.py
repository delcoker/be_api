from typing import List, Optional

from pydantic import BaseModel

class ScopeBase(BaseModel):
    name: str
    scope: str

class ScopeCreate(ScopeBase):
    user_id: int

    class Config:
        orm_mode = True

class Scope(ScopeCreate):
    id: int

    class Config:
        orm_mode = True
