from typing import List, Optional

from pydantic import BaseModel
from core.schemas.keywords import Keyword

class CategoryBase(BaseModel):
    category_name	: str


class CategoryCreate(CategoryBase):
    group_category_id: int
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True

class Category(CategoryCreate):
    id: int
    group_category_id: int

    class Config:
        orm_mode = True
