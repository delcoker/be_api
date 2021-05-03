from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Form
from typing import List
from sqlalchemy.orm import Session


from controllers import crud
from core.schemas import group_categories
from core.models.database import SessionLocal, engine
# from dependency.dependencies import get_db

router = APIRouter()

#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to store group categories
@router.post("/group/category/create/", response_model=group_categories.GroupCategory)
def group_category_create(group_category: group_categories.GroupCategoryCreate, db: Session = Depends(get_db)):
    return crud.create_group_category(db, group_category)

# Route to get group categories
@router.get("/group/categories/", response_model=List[group_categories.GroupCategory])
def get_group_categories(db: Session = Depends(get_db)):
    group_categories = crud.get_group_categories(db)
    return group_categories

# Get specified group category
@router.get("/group/category/{group_category_id}", response_model=group_categories.GroupCategory)
def read_group_category(group_category_id: int, db: Session = Depends(get_db)):
    db_group_category = crud.get_group_category(
        db, group_category_id=group_category_id)
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category not found")
    return db_group_category

# Update specified group category
@router.post("/group/category/update/{group_category_id}")# , response_model=group_categories.GroupCategory
def update_group_category(group_category_id: int, group_category: group_categories.GroupCategoryCreate, db: Session = Depends(get_db)):
    db_group_category = crud.update_group_category(
        db, group_category_id, group_category)
    if db_group_category is None:
        raise HTTPException(status_code=404, detail="Group Category not found")
    return {"message": "Group Category has been updated succesfully"}

# Delete specified group category
@router.post("/group/category/delete/{group_category_id}")
def delete_group_category(group_category_id: int, db: Session = Depends(get_db)):
    db_group_category = crud.delete_group_category(db, group_category_id)
    if db_group_category == 1:
        return {"message": "Group Category has been deleted succesfully"}
