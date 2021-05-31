from controllers.streams_controller import MyTwitter
from fastapi import FastAPI
# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv
# Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from starlette.middleware.sessions import SessionMiddleware
load_dotenv()

app = FastAPI()
# Created a session middleware  
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET_KEY'))
app.add_middleware(DBSessionMiddleware, db_url=os.getenv('MYSQLURLPATH'))

twitter_streamer = MyTwitter()
# twitter_streamer.worker()