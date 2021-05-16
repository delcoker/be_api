from sqlalchemy.orm import Session
# Import model and schemas from other folders
from core.models import users
from core.schemas import user_schemas
from core.schemas import group_categories
from core.models.database import SessionLocal, engine

# Import OAuth2 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt
# Allowing you to use different hashing algorithms
from passlib.context import CryptContext
# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Test for stream
import requests
import json
import base64
# Test for stream end


from typing import Optional

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
SECRET_KEY = os.getenv('SECRET_KEY')
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

# Retrieve a user based on their email
# def get_user(db: Session, email: str):
#     return db.query(users.User).filter(users.User.email==email)

def get_user_by_email(db: Session, email: str):
    return db.query(users.User).filter(users.User.email == email).first()

def create_user(db: Session, first_name: str, last_name: str, email: str, phone: str, password: str):
    db_user = users.User(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        password=get_password_hash(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_group_category = users.GroupCategory(
        user_id = db_user.id,
        group_category_name = "Topic"
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
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session, token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY,
                             algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        # return email
        if email is None:
            raise credentials_exception
        # token_data = TokenData(username=username)
        token_data = email
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data)
    if user is None:
        raise credentials_exception
    return user


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
    db_social_user = users.SocialAccount(
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
    return db.query(users.User).filter(users.User.id == user_id).first()


def get_users(db: Session):  # , skip: int = 0, limit: int = 100
    # Limit and offset works like pagination
    # return db.query(users.User).offset(skip).limit(limit).all()
    return db.query(users.User).all()

# Code for generating bearer token
def generate_bearer_token():
    bearer_token = base64.b64encode(
        f"{os.getenv('TWITTER_CLIENT_ID')}:{os.getenv('TWITTER_CLIENT_SECRET')}".encode())
    headers = {
        "Authorization": f"Basic {bearer_token.decode()}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    resp = requests.post(
        url="https://api.twitter.com/oauth2/token",
        data={"grant_type": "client_credentials"},
        headers=headers,
    )
    data = resp.json()

    return data

# Code for creating group category
def create_group_category(db: Session, group_category_name: str, token:str):
    user = get_current_user(db, token)
    db_group_category = users.GroupCategory(
        user_id= user.id,
        group_category_name = group_category_name
    )
    db.add(db_group_category)
    db.commit()
    db.refresh(db_group_category)
    return db_group_category

# Get all Group Categories
def get_group_categories(db: Session, token:str):
    user = get_current_user(db, token)
    # Limit and offset works like pagination
    return db.query(users.GroupCategory).filter(users.GroupCategory.user_id == user.id).all()


def get_group_category(db: Session, token: str, group_category_id: int):
    user = get_current_user(db, token)
    return db.query(users.GroupCategory).filter(users.GroupCategory.id == group_category_id, users.GroupCategory.user_id == user.id).first()


def update_group_category(db: Session, group_category_id: int, group_category_name: str):
    result = db.query(users.GroupCategory).filter(users.GroupCategory.id == group_category_id).update({
        "group_category_name": group_category_name
    })
    db.commit()
    return result


def delete_group_category(db: Session, group_category_id: int):
    # get_current_user(db, token)
    result = db.query(users.GroupCategory).filter(users.GroupCategory.id == group_category_id).delete()
    db.commit()
    return result

# Code for creating headers to connect to twitter for the streams
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

# Get the rules that are stored by twitter for user account
def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()

# Delete the rules stored by twitter for this user
def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

# Code for setting the rules needed by twitter to start the fetch
def set_rules(headers, delete, bearer_token):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "#ecg"},
        {"value": "#esl"},
        {"value": "#dumsor"},
        # {"value": "dog has:images", "tag": "dog pictures"},
        # {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    print(json.dumps(response.json()))

# Start getting tweets that contain the rules specified
def get_stream(headers, set, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent=4, sort_keys=True))

