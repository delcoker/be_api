from typing import List, Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    category_name	: str


class CategoryCreate(GroupCategoryBase):
    group_category_id: int

    class Config:
        orm_mode = True

class Category(CategoryBase):
    id: int
    group_category_id: int

    class Config:
        orm_mode = True
