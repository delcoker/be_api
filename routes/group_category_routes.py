from typing import List

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette.requests import Request

from auth import auth
from auth.auth import get_db
from controllers import group_category_controller
from core.schemas import group_categories_dto

# from services.dependencies import get_db
router = APIRouter(tags=["Group Categories"],
                   dependencies=[Depends(auth.get_user_from_token)])


# Route to store group categories
@router.post("/group/category/create", response_model=group_categories_dto.GroupCategoryList)
def group_category_create(req: Request, group_category_name: str = Form(...), db: Session = Depends(get_db)):
    db_group_category = group_category_controller.create_group_category(
        db, group_category_name, req.headers['token'])
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category could not be created")
    return db_group_category


# Route to get group categories
@router.get("/group/categories", response_model=List[group_categories_dto.GroupCategoryList])
def get_group_categories(req: Request, db: Session = Depends(get_db)):
    group_categories = group_category_controller.get_group_categories(db, req.headers['token'])
    return group_categories


# Get specified group category
@router.get("/group/category/{group_category_id}", response_model=group_categories_dto.GroupCategoryList)
def read_group_category(group_category_id: int, req: Request, db: Session = Depends(get_db)):
    db_group_category = group_category_controller.get_group_category(
        db, req.headers['token'], group_category_id=group_category_id)
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category not found")
    return db_group_category


# Update specified group category
@router.post("/group/category/update/{group_category_id}")  # , response_model=group_categories.GroupCategory
def update_group_category(req: Request, group_category_id: int, group_category_name: str = Form(...), db: Session = Depends(get_db)):
    db_group_category = group_category_controller.update_group_category(
        db, group_category_id, group_category_name, req.headers['token'])
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category not found")
    return {"message": "Group Category has been updated successfully"}


# Delete specified group category
@router.post("/group/category/delete/{group_category_id}")
def delete_group_category(req: Request, group_category_id: int, db: Session = Depends(get_db)):
    db_group_category = group_category_controller.delete_group_category(db, group_category_id, req.headers['token'])
    if db_group_category == 1:
        return {"message": "Group Category has been deleted successfully"}
    elif db_group_category == 2:
        return {"message": "Group Category must contain at least one value for user"}
