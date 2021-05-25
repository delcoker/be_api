# System Imports
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status, Form
from sqlalchemy.orm import Session

# Custom Imports
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt  # Encoding and decoding jwt
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# Using OAuth1Session
from requests_oauthlib import OAuth1Session, OAuth1
# Using OAuth1 auth helper
import requests
from urllib.parse import urlencode, urljoin, parse_qs
from core.schemas.user_schemas import Url
import base64
# from fastapi.security import OAuth2PasswordBearer

# Controllers
from controllers import crud, streams_controller
from controllers.streams_controller import MyTwitter

# Models
from core.models import users

# Routes
from routers import auth_routes, group_category_routes, category_routes, scope_routes, user_routes

# Database
from core.models.database import SessionLocal, engine

# Dependency
from dependency.dependencies import get_user_token

# Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper

# Creating a fastapi instance
app = FastAPI()

load_dotenv()
# Created a session middleware  
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY'))
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('MYSQLURLPATH'))
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

users.Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(group_category_routes.router)
app.include_router(category_routes.router)
app.include_router(scope_routes.router)
app.include_router(user_routes.router)

@app.on_event("startup")
async def start_stream(db: Session = Depends(get_db)):
    MyTwitter()

# @app.get("/stream") # , dependencies=[Depends(get_user_token)]
# def main(req: Request, db: Session = Depends(get_db)):
    # headers = streams_controller.create_headers(bearer_token)
    # rules = streams_controller.get_rules(headers, bearer_token)
    # delete = streams_controller.delete_all_rules(headers, bearer_token, rules)
    # set = streams_controller.set_rules(headers, delete, bearer_token, db)
    # streams_controller.get_stream(headers, set, bearer_token, db)#, req.headers['token']
