from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, Form
from sqlalchemy.orm import Session

from controllers import crud
from core.schemas import user_schemas
from core.models import users
from core.models.database import SessionLocal, engine
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt  # Encoding and decoding jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

# Import os and dotenv to read data from env file
import os

from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

# Using OAuth1 auth helper
import requests
from requests_oauthlib import OAuth1

from urllib.parse import urlencode, urljoin, parse_qs

from fastapi.middleware.cors import CORSMiddleware

from core.schemas.user_schemas import Url

authenticate_url = 'https://api.twitter.com/oauth/authenticate'
authorize_url = 'https://api.twitter.com/oauth/authorize'
request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'

# oauth = OAuth()
# oauth.register(
#     name='twitter',
#     client_id=os.getenv('TWITTER_CLIENT_ID'),
#     client_secret=os.getenv('TWITTER_CLIENT_SECRET'),
#     api_base_url='https://api.twitter.com/1.1/',
# )

users.Base.metadata.create_all(bind=engine)

# Creating a fastapi instance
app = FastAPI()

# Created a session middleware  
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY'))

origins = [
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/login", response_model=user_schemas.Logged_In_User)
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


@app.post("/users/me/", response_model=user_schemas.UserBase)
def read_users_me(token: user_schemas.Token, db: Session = Depends(get_db)):
    current_user: users.User = crud.get_current_user(db, token)
    return current_user


@app.post("/register", response_model=user_schemas.UserBase)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get('/login/twitter')
async def login_via_twitter(request: Request):
    oauth = OAuth1Session(os.getenv('TWITTER_CLIENT_ID'), client_secret=os.getenv('TWITTER_CLIENT_SECRET'))
    fetch_response = oauth.fetch_request_token(request_token_url)
    return Url(url=authorize_url + '?oauth_token=' + fetch_response.get(
        'oauth_token') + '&oauth_token_secret=' + fetch_response.get('oauth_token_secret'))


@app.post('/auth/twitter')
# Receive request and token from fe and start a db session 
async def auth_via_twitter(token: str = Form(...), oauth_token: str = Form(...),
                           oauth_verifier: str = Form(...),
                           db: Session = Depends(get_db)):
    # Fetch token and verifier and pass to oauth function
    oauth = OAuth1Session(os.getenv('TWITTER_CLIENT_ID'),
                               client_secret=os.getenv('TWITTER_CLIENT_SECRET'),
                               resource_owner_key=oauth_token,
                               verifier=oauth_verifier)
    # get access tokens
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    # account name
    account = "twitter"
    # Send details to the function that stores the information of the user and their social media details
    db_social_account = crud.store_user_social_account(db, oauth_tokens.get('oauth_token'), oauth_tokens.get('oauth_token_secret'), token, account)
    # Return response/data after the function stores the details
    return db_social_account


@app.get("/users/", response_model=List[user_schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=user_schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# @app.get()
# def read_users_social_accounts
