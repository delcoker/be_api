from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Form
from typing import List
from sqlalchemy.orm import Session
from starlette.requests import Request

# Custom
from controllers import scopes_controller
from dependency.dependencies import get_user_token
from core.models.database import SessionLocal, engine
from core.schemas import scopes


router = APIRouter(
    prefix="/scopes",
    tags=["Scopes"],
    dependencies=[Depends(get_user_token)]
)

#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to store a scope
@router.post("/create")
def scope_create(req: Request, scope_name: str = Form(...), scope: str = Form(...), db: Session = Depends(get_db)):
    db_scope = scopes_controller.create_scope(
        db, scope_name, scope, req.headers['token'])
    if db_scope is None:
        raise HTTPException(status_code=404, detail="Group Category could not be created")
    return {"message": "Scope created succesfully"}

# Route to get scopes
@router.get("/", response_model=List[scopes.Scope])
def get_scopes(req: Request, db: Session = Depends(get_db)):
    scopes = scopes_controller.get_scopes(db, req.headers['token'])
    return scopes

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
    return {"message": "Group Category has been updated succesfully"}

# Delete specified group category
@router.post("/group/category/delete/{group_category_id}")
def delete_group_category(group_category_id: int, db: Session = Depends(get_db)):
    db_group_category = crud.delete_group_category(db, group_category_id)
    if db_group_category == 1:
        return {"message": "Group Category has been deleted succesfully"}

