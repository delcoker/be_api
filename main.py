# System Imports
from fastapi import FastAPI

# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# Routes
from routers import auth_routes, group_category_routes, category_routes, scope_routes, user_routes

# Middleware
from fastapi.middleware.cors import CORSMiddleware

# Necessary to get details from env
load_dotenv()

# Create Instance of FastAPI
app = FastAPI()

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

# config = Config()
# config.bind = ["127.0.0.1:8000"] 
# asyncio.run(serve(app, config))

app.include_router(auth_routes.router)
app.include_router(group_category_routes.router)
app.include_router(category_routes.router)
app.include_router(scope_routes.router)
app.include_router(user_routes.router)