from fastapi import APIRouter, Depends, HTTPException, Form
from typing import List
from sqlalchemy.orm import Session
from starlette.requests import Request

from controllers import category_controller
from auth import auth
from core.schemas import categories_dto, posts_dto
from core.models.database import SessionLocal

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(auth.get_user_from_token)]
)


#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Route to get all categories
@router.get("", response_model=List[categories_dto.CategoryDto])
def get_all_categories(req: Request, db: Session = Depends(get_db)):
    categories = category_controller.get_all_categories(db, req.headers['token'])
    return categories


# Route to create a category
@router.post("/create", response_model=categories_dto.CategoryDto)
def create_category(category_name: str = Form(...), group_category_id: int = Form(...), keywords: str = Form(None),
                    db: Session = Depends(get_db)):
    created_category = category_controller.create_category(db, category_name, group_category_id, keywords)
    return created_category


# Get specified category
@router.get("/{category_id}", response_model=categories_dto.CategoryDto)
def read_category(req: Request, category_id: int, db: Session = Depends(get_db)):
    db_category = category_controller.get_category(
        db, req.headers['token'], category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category


# Update specified category
@router.post("/update/{category_id}")
def update_category(category_id: int, category_name: str = Form(...), group_category_id: int = Form(...),
                    keywords: str = Form(...), db: Session = Depends(get_db)):
    db_category = category_controller.update_category(db, category_id, category_name, group_category_id, keywords)
    if db_category is None:
        raise db_category(status_code=404, detail="Category not found")
    return {"message": "Category has been updated."}


# Delete specified category
@router.post("/delete/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = category_controller.delete_category(db, category_id)
    if db_category == 1:
        return {"message": "Category has been deleted"}


# get post regarding a specified category
@router.post("/posts/{category_id}", response_model=List[posts_dto.PostDto])
def get_category_posts(category_id: int, db: Session = Depends(get_db)):
    db_category = category_controller.get_category_posts(category_id, db)
    return db_category
