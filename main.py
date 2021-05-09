from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, Form
from sqlalchemy.orm import Session

from controllers import crud
from core.models import users
from routers import auth_routes, group_category_routes, category_routes, scope_routes, user_routes
from core.models.database import SessionLocal, engine
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt  # Encoding and decoding jwt


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
import base64

authenticate_url = 'https://api.twitter.com/oauth/authenticate'
authorize_url = 'https://api.twitter.com/oauth/authorize'
request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'

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


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

app.include_router(auth_routes.router)
app.include_router(group_category_routes.router)
app.include_router(category_routes.router)
app.include_router(scope_routes.router)
app.include_router(user_routes.router)


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
    db_social_account = crud.store_user_social_account(db, oauth_tokens.get('oauth_token'),
                                                       oauth_tokens.get('oauth_token_secret'), token, account)
    # Return response/data after the function stores the details
    return db_social_account

# @app.get("/users/group/category/{user_id}", response_model=user_schemas.User_Group_Categories)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.create_group_category(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


@app.get("/stream")
def main():
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAAR4GwEAAAAAgkH0ksQzl%2B7Kwa9xMK4yXVdrci4%3DZaRE7GIRRMvm2VwcqvzV7zrpcaL6BqUvUfwHZk5aUZzf4ON0Ev"
    # bearer_token = "AAAAAAAAAAAAAAAAAAAAAKd99QAAAAAAFT%2BLsnpKWIBwEp3XSOP%2ByOViZes%3DtR26nwuAlgFIEV25QpLozw4p4Zn9xxzKYAAeVvkIRT7fbEu8R2"
    headers = crud.create_headers(bearer_token)
    rules = crud.get_rules(headers, bearer_token)
    delete = crud.delete_all_rules(headers, bearer_token, rules)
    set = crud.set_rules(headers, bearer_token)
    crud.get_stream(headers, set, bearer_token)
