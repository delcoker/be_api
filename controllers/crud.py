# Import os and dotenv to read data from env file
import os
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Header
# Import OAuth2
from fastapi.security import OAuth2PasswordBearer
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt
# Allowing you to use different hashing algorithms
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Import model and schemas from other folders
from core.models import schema
from core.models.database import SessionLocal

load_dotenv()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"

# Hash password coming from user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Instance of OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login")  # URL that the client will use to send details in order to get a token


# Utility to verify if a received password matches the hash stored
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# Connection fetch token and verify
def get_user_token(db: Session = Depends(get_db), token: str = Header(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        # return email
        if email is None:
            raise credentials_exception
        token_data = email
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data)
    if user is None:
        raise credentials_exception
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(schema.User) \
        .filter(schema.User.email == email) \
        .first()


def create_user(db: Session, first_name: str, last_name: str, email: str, phone: str, password: str):
    db_user = schema.User(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        password=get_password_hash(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_group_category = schema.GroupCategory(
        user_id=db_user.id,
        group_category_name="Topics"
    )
    db.add(db_group_category)
    db.commit()
    db.refresh(db_group_category)
    return db_user


# Authenticate and return a user
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=os.getenv('JWT_EXPIRATION_TIME'))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def store_user_social_account(db: Session, oauth_token: str, oauth_token_secret: str, token: str, account_name: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY,
                             algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
        token_data = email
    except JWTError:
        raise credentials_exception
    # return token_data
    user = get_user_by_email(db, email=token_data)
    if user is None:
        raise credentials_exception
    # return twitter_user_details["oauth_token"]
    db_social_user = schema.SocialAccount(
        user_id=user.id,
        name=account_name,
        oauth_token=oauth_token,
        oauth_token_secret=oauth_token_secret,
    )
    db.add(db_social_user)
    db.commit()
    db.refresh(db_social_user)
    return db_social_user


def get_user(db: Session, user_id: int):
    # return db.query(users.User).filter(users.User.id == user_id).first()
    return db.query(schema.User) \
        .filter(schema.User.id == user_id) \
        .first()


def get_users(db: Session):  # , skip: int = 0, limit: int = 100
    # Limit and offset works like pagination
    # return db.query(users.User).offset(skip).limit(limit).all()
    return db.query(schema.User).all()
