from typing import List
# Import fastapi and others
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from controllers import crud
from core.schemas import user_schemas
from core.models import users
from core.models.database import SessionLocal, engine
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt # Encoding and decoding jwt
# Import OAuth2
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta


users.Base.metadata.create_all(bind=engine)

# Creating a fastapi instance
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


ACCESS_TOKEN_EXPIRE_MINUTES = 30 
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


@app.post("/login", response_model=user_schemas.Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.authenticate_user(
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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=user_schemas.User)
# async def read_users_me(current_user: users.User = Depends(get_current_active_user)):
def read_users_me(user: user_schemas.UserBase = Depends(crud.get_current_user)):
    # current_user: users.User = crud.get_current_user()
    return user

@app.post("/register", response_model=user_schemas.UserBase)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=List[user_schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/users/{user_id}", response_model=user_schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

