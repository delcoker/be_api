from typing import List, Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    category_name	: str


class CategoryCreate(CategoryBase):
    group_category_id: int

    class Config:
        orm_mode = True

class Category(CategoryCreate):
    id: int
    group_category_id: int

    class Config:
        orm_mode = True
