import os
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session

# Custom
from core.models.database import SessionLocal
from auth import auth
from core.schemas import user_schemas_dto


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRATION_TIME'))

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/rules")
def test():
    return "OK"

# Create user
@router.post("/register", response_model=user_schemas_dto.User)
def create_user(first_name: str = Form(...), last_name: str = Form(...), email: str = Form(...), phone: str = Form(...), password: str = Form(...),  db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = auth.create_user(db, first_name, last_name, email, phone, password)
    return created_user  # , "status_code": 200


# User login
@router.post("/login", response_model=user_schemas_dto.Logged_In_User)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user: user_schemas_dto.Logged_In_User = auth.authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    user.token = access_token
    user.token_type = "bearer"
    return user
