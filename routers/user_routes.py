from fastapi import APIRouter, Depends, HTTPException, Form
from typing import List
from sqlalchemy.orm import Session
from starlette.requests import Request

# Custom
from core.models.database import SessionLocal
from controllers import users_controller
from auth import auth
# from dependency.dependencies import get_user_token
from core.schemas import user_schemas_dto
from core.models import schema

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(auth.get_user_token)]
)


#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fetch all users
@router.get("", response_model=List[user_schemas_dto.User])
# def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
def get_users(db: Session = Depends(get_db)):
    users = auth.get_users(db)  # skip=skip, limit=limit
    return users


# Return current user data
@router.post("/user/me", response_model=user_schemas_dto.User)
def read_users_me(req: Request, db: Session = Depends(get_db)):
    print("IS THIS BEING USED")
    current_user: schema.User = auth.get_current_user(db, req.headers['token'])
    return current_user


@router.get("/{user_id}", response_model=user_schemas_dto.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/update/{user_id}")
def update_user(user_id: int, first_name: str = Form(...),
                last_name: str = Form(...), phone: str = Form(...),
                db: Session = Depends(get_db)):
    db_user = users_controller.update_user(db, user_id, first_name, last_name, phone)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not updated")
    return db_user
