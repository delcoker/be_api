from typing import List, Optional

from pydantic import BaseModel

class KeywordBase(BaseModel):
    keywords: str

class KeywordCreate(KeywordBase):
    category_id: Optional[int]

    class Config:
        orm_mode = True

class Keyword(KeywordCreate):
    id: Optional[int]

    class Config:
        orm_mode = True
