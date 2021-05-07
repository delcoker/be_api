from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Form
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Custom
from core.models.database import SessionLocal, engine
from controllers import crud
from core.schemas import user_schemas


ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_user_token)]
)

#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create user
@router.post("/register", response_model=user_schemas.UserBase)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# User login
@router.post("/login", response_model=user_schemas.Logged_In_User)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user: user_schemas.Logged_In_User = crud.authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    user.token = access_token
    user.token_type = "bearer"
    return user

# Fetch all users
@router.get("/", response_model=List[user_schemas.User])
# def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
def get_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)  # skip=skip, limit=limit
    return users

# Return current user data
@router.post("/user/me/", response_model=user_schemas.User)
def read_users_me(token: str = Form(...), db: Session = Depends(get_db)):
    current_user: users.User = crud.get_current_user(db, token)
    return current_user

@router.get("/{user_id}", response_model=user_schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
