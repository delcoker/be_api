from typing import Optional

from pydantic import BaseModel


class KeywordBase(BaseModel):
    keywords: Optional[str]


class KeywordCreate(KeywordBase):
    category_id: int

    class Config:
        orm_mode = True


class Keyword(KeywordCreate):
    id: int

    class Config:
        orm_mode = True
