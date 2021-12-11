from typing import List, Optional

from pydantic import BaseModel
from core.schemas.categories_dto import CategoryDto


class GroupCategoryBase(BaseModel):
    group_category_name: str


class GroupCategoryCreate(GroupCategoryBase):
    user_id: int

    class Config:
        orm_mode = True


class GroupCategory(GroupCategoryBase):
    id: int
    user_id: int


class GroupCategoryList(GroupCategory):
    categories: List[CategoryDto] = []

    class Config:
        orm_mode = True
