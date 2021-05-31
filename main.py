# System Imports
from fastapi import FastAPI

# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# Routes
from routers import auth_routes, group_category_routes, category_routes, scope_routes, user_routes

# Middleware
from fastapi.middleware.cors import CORSMiddleware

# Asyncio
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from starlette.middleware.sessions import SessionMiddleware

# Necessary to get details from env
load_dotenv()

# Create Instance of FastAPI
app = FastAPI()

origins = [
# "http://localhost.tiangolo.com",
# "https://localhost.tiangolo.com",
# "http://localhost",
# "http://localhost:8080",
# "https://dwm-social-media-frontend.herokuapp.com",
"*"
]

app.add_middleware(
CORSMiddleware,
allow_origins=origins,
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=os.getenv('JWT_SECRET_KEY'))
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('MYSQLURLPATH'))

app.include_router(auth_routes.router)
app.include_router(group_category_routes.router)
app.include_router(category_routes.router)
app.include_router(scope_routes.router)
app.include_router(user_routes.router)

# @app.get('/login/twitter')
# async def login_via_twitter(request: Request):
#     oauth = OAuth1Session(os.getenv('TWITTER_CLIENT_ID'), client_secret=os.getenv('TWITTER_CLIENT_SECRET'))
#     fetch_response = oauth.fetch_request_token(request_token_url)
#     return Url(url=authorize_url + '?oauth_token=' + fetch_response.get(
#         'oauth_token') + '&oauth_token_secret=' + fetch_response.get('oauth_token_secret'))
#
#
# @app.post('/auth/twitter')
# # Receive request and token from fe and start a db session
# async def auth_via_twitter(token: str = Form(...), oauth_token: str = Form(...),
#                            oauth_verifier: str = Form(...),
#                            db: Session = Depends(get_db)):
#     oauth = OAuth1Session(os.getenv('TWITTER_CLIENT_ID'), client_secret=os.getenv('TWITTER_CLIENT_SECRET'))
#     fetch_response = oauth.fetch_request_token(request_token_url)
#
#     oauth = OAuth1Session(os.getenv('TWITTER_CLIENT_ID'),
#                                client_secret=os.getenv('TWITTER_CLIENT_SECRET'),
#                                resource_owner_key=oauth_token,
#                                verifier=oauth_verifier)
#     oauth_tokens = oauth.fetch_access_token(access_token_url)
#     print(oauth_tokens)
#     # account name
#     account = "twitter"
#     # Send details to the function that stores the information of the user and their social media details
#     db_social_account = crud.store_user_social_account(db, oauth_tokens.get('oauth_token'),oauth_tokens.get('oauth_token_secret'), token, account)
#     # Return response/data after the function stores the details
#     return db_social_account

config = Config()
port = int(os.environ.get("PORT", 8000))
config.bind = [f'0.0.0.0:{port}']
asyncio.run(serve(app, config))
