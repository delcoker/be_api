from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Form
from typing import List
from sqlalchemy.orm import Session


from controllers import crud, category_controller
from core.schemas import categories
from core.models.database import SessionLocal, engine
from dependency.dependencies import get_user_token

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    # dependencies=[Depends(get_user_token)]
    )

#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to get all categories
@router.get("/", response_model=List[categories.Category])
def get_all_categories(db: Session = Depends(get_db)):
    categories = category_controller.get_all_categories(db)
    return categories

# Route to create a category
@router.post("/create", response_model=categories.Category)
def create_category(category: categories.CategoryCreate, db: Session = Depends(get_db)):
    return category_controller.create_category(db, category)

# Get specified category
@router.get("/{category_id}", response_model=categories.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = category_controller.get_category(
        db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# Update specified category
@router.post("/update/{category_id}")
def update_category(category_id: int, category: categories.CategoryCreate, db: Session = Depends(get_db)):
    db_category = category_controller.update_category(
        db, category_id, category)
    if db_category is None:
        raise db_category(status_code=404, detail="Category not found")
    return {"message": "Category has been updated succesfully"}

# Delete specified category
@router.post("/delete/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = category_controller.delete_category(db, category_id)
    if db_category == 1:
        return {"message": "Category has been deleted succesfully"}

# # , response_model=group_categories.GroupCategory
# @router.post("/group/category/update/{group_category_id}")
# def update_group_category(group_category_id: int, group_category: group_categories.GroupCategoryCreate, db: Session = Depends(get_db)):
#     db_group_category = crud.update_group_category(
#         db, group_category_id, group_category)
#     if db_group_category is None:
#         raise HTTPException(status_code=404, detail="Group Category not found")
#     return {"message": "Group Category has been updated succesfully"}

# # Delete specified group category


# @router.post("/group/category/delete{group_category_id}")
# def delete_group_category(group_category_id: int, db: Session = Depends(get_db)):
#     db_group_category = crud.delete_group_category(db, group_category_id)
#     if db_group_category == 1:
#         return {"message": "Group Category has been deleted succesfully"}
