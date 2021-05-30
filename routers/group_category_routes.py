from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Form
from typing import List
from sqlalchemy.orm import Session
from starlette.requests import Request


from controllers import crud
from core.schemas import group_categories
from core.models.database import SessionLocal, engine
from dependency.dependencies import get_user_token

# from dependency.dependencies import get_db
router = APIRouter(tags=["Group Categories"],
                   dependencies=[Depends(get_user_token)])

#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to store group categories
@router.post("/group/category/create", response_model=group_categories.GroupCategoryList)
def group_category_create(req: Request, group_category_name: str = Form(...), db: Session = Depends(get_db)):
    db_group_category = crud.create_group_category(
        db, group_category_name, req.headers['token'])
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category could not be created")
    return db_group_category

# Route to get group categories
@router.get("/group/categories", response_model=List[group_categories.GroupCategoryList])
def get_group_categories(req: Request, db: Session = Depends(get_db)):
    group_categories = crud.get_group_categories(db, req.headers['token'])
    return group_categories

# Get specified group category
@router.get("/group/category/{group_category_id}", response_model=group_categories.GroupCategoryList)
def read_group_category(group_category_id: int, req: Request, db: Session = Depends(get_db)):
    db_group_category = crud.get_group_category(
        db, req.headers['token'], group_category_id=group_category_id)
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category not found")
    return db_group_category

# Update specified group category
@router.post("/group/category/update/{group_category_id}")# , response_model=group_categories.GroupCategory
def update_group_category(group_category_id: int, group_category_name: str = Form(...), db: Session = Depends(get_db)):
    db_group_category = crud.update_group_category(
        db, group_category_id, group_category_name)
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category not found")
    return {"message": "Group Category has been updated successfully"}

# Delete specified group category
@router.post("/group/category/delete/{group_category_id}")
def delete_group_category(group_category_id: int, db: Session = Depends(get_db)):
    db_group_category = crud.delete_group_category(db, group_category_id)
    if db_group_category == 1:
        return {"message": "Group Category has been deleted successfully"}
