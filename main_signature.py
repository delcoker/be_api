"""

import base64
import binascii
import hashlib
import hmac
import urllib
from typing import List
# Import fastapi and others
from fastapi import Depends, FastAPI, HTTPException, status, Form
from sqlalchemy.orm import Session

from urllib.parse import urlencode

from auth import auth
from core.schemas import user_schemas_dto
from core.models import schema
from core.models.database import SessionLocal, engine
# Import JWT and authentication dependencies needed
# Import OAuth2
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

# Import os and dotenv to read data from env file
import os

from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
import requests  # Used for post requests for the twitter api connection
import time  # This is for generating timestamp value

from fastapi.middleware.cors import CORSMiddleware

authenticate_url = 'https://api.twitter.com/oauth/authenticate'
authorize_url = 'https://api.twitter.com/oauth/authorize'
request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'

oauth = OAuth()
oauth.register(
    name='twitter',
    client_id=os.getenv('TWITTER_CLIENT_ID'),
    client_secret=os.getenv('TWITTER_CLIENT_SECRET'),
    api_base_url='https://api.twitter.com/1.1/',
)

schema.Base.metadata.create_all(bind=engine)

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


@app.post("/login", response_model=user_schemas_dto.LoggedInUser)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user: user_schemas_dto.LoggedInUser = auth.authenticate_user(
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
    user.access_token = access_token
    user.token_type = "bearer"
    return user


@app.post("/users/me/", response_model=user_schemas_dto.UserBase)
def read_users_me(token: user_schemas_dto.Token, db: Session = Depends(get_db)):
    current_user: schema.User = auth.get_current_user(db, token)
    return current_user


@app.post("/register", response_model=user_schemas_dto.UserBase)
def create_user(user: user_schemas_dto.UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user)


@app.get('/login/twitter')
async def login_via_twitter(request: Request):
    payload = {}
    files = {}
    # Create timestamp
    auth_time = int(time.time())
    grant_type = 'client_credentials'
    oauth_consumer_key = os.getenv('TWITTER_CLIENT_ID')  # From credentials.properties file
    oauth_nonce = str(int(time.time() * 1000))
    oauth_signature_method = 'HMAC-SHA1'
    oauth_timestamp = str(int(time.time()))
    oauth_version = '1.0'

    parameter_string = create_parameter_string(grant_type, oauth_consumer_key, oauth_nonce, oauth_signature_method,
                                               oauth_timestamp, oauth_version)

    encoded_parameter_string = urllib.parse.quote(parameter_string, safe='')
    encoded_base_string = 'POST' + '&' + urllib.parse.quote(request_token_url, safe='')
    encoded_base_string = encoded_base_string + '&' + encoded_parameter_string

    access_key_secret = os.getenv('TWITTER_CLIENT_SECRET')  # From credentials.properties file
    signing_key = access_key_secret + '&'

    oauth_signature = create_signature(signing_key, encoded_base_string)

    print(oauth_signature)

    encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe='')


    # Headers being passed to url
    headers = {
        'Authorization': 'OAuth oauth_consumer_key=' + os.getenv('TWITTER_CLIENT_ID') + ','
                         'oauth_signature_method="HMAC-SHA1",'
                         'oauth_timestamp="'+oauth_timestamp+'",'
                         'oauth_nonce="'+oauth_nonce+'",'
                         'oauth_version="1.0",'
                         'oauth_callback="http%3A%2F%2Flocalhost%3A8000%2Fauth%2Ftwitter",'
                         'oauth_signature="'+encoded_oauth_signature+'"',
    }

    headers = {
        'Authorization': 'OAuth oauth_consumer_key="'+os.getenv('TWITTER_CLIENT_ID')+'",oauth_signature_method="HMAC-SHA1",oauth_timestamp="'+oauth_timestamp+'",oauth_nonce="'+oauth_nonce+'",oauth_version="1.0",oauth_callback="http%3A%2F%2Flocalhost%3A8000%2Fauth%2Ftwitter",oauth_signature="'+encoded_oauth_signature+'"',
    }

    # Go to url with paramters
    response = requests.request("POST", request_token_url, headers=headers, data=payload, files=files)
    # Return with callback and token for redirect and send to client
    # print(str(auth_time))
    print(response.text)
    print(headers)
    return headers
    # return Url(url=authorize_url +'?'+ response.text)



@app.get('/auth/twitter')
# Receive request and token from fe and start a db session
async def auth_via_twitter(token: str = Form(...), oauth_token: str = Form(...), oauth_verifier: str = Form(...),
                           db: Session = Depends(get_db)):
    params = {"oauth_consumer_key": os.getenv('TWITTER_CLIENT_ID'),
              "oauth_token": oauth_token,
              "oauth_verifier": oauth_verifier
              }
    inp_post_response = requests.post(request_token_url, params=params)
    account = "twitter"
    # Send details to the function that stores the information of the user and their social media details
    db_social_account = auth.store_user_social_account(db, inp_post_response.oauth_token, inp_post_response.oauth_token_secret, token, account)
    # Return response/data after the function stores the details
    return db_social_account


@app.get("/users/", response_model=List[user_schemas_dto.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = auth.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=user_schemas_dto.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version):
    parameter_string = ''
    # parameter_string = parameter_string + 'grant_type=' + grant_type
    parameter_string = parameter_string + '&oauth_consumer_key=' + oauth_consumer_key
    parameter_string = parameter_string + '&oauth_nonce=' + oauth_nonce
    parameter_string = parameter_string + '&oauth_signature_method=' + oauth_signature_method
    parameter_string = parameter_string + '&oauth_timestamp=' + oauth_timestamp
    parameter_string = parameter_string + '&oauth_version=' + oauth_version
    return parameter_string

def create_signature(secret_key, signature_base_string):
    encoded_string = signature_base_string.encode()
    encoded_key = secret_key.encode()
    temp = hmac.new(encoded_key, encoded_string, hashlib.sha1).hexdigest()
    byte_array = base64.b64encode(binascii.unhexlify(temp))
    return byte_array.decode()


# @app.get()
# def read_users_social_accounts

# Receive request and token from fe and start a db session
async def auth_via_twitter(token: str = Form(...), oauth_token: str = Form(...), oauth_verifier: str = Form(...),
                           # Using OAuth1Session
                           oauth=OAuth1Session(os.getenv('TWITTER_CLIENT_ID'),
                                               client_secret=client_secret,
                                               resource_owner_key=resource_owner_key,
                                               resource_owner_secret=resource_owner_secret,
                                               verifier=verifier)

    oauth_tokens = oauth.fetch_access_token(access_token_url)


account = "twitter"
# Send details to the function that stores the information of the user and their social media details
db_social_account = auth.store_user_social_account(db, inp_post_response.oauth_token,
                                                   inp_post_response.oauth_token_secret, token, account)
# Return response/data after the function stores the details
return db_social_account

"""