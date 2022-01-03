from typing import List

from pydantic import BaseModel
from core.schemas.keywords_dto import Keyword


class CategoryBase(BaseModel):
    category_name: str


class CategoryCreate(CategoryBase):
    group_category_id: int
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True


class CategoryDto(CategoryCreate):
    id: int
    group_category_id: int

    class Config:
        orm_mode = True
