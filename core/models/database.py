from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()


# SQLALCHEMY_DATABASE_URL = "mysql+mysqldb://root:''@127.0.0.1[:3306]/user_management"
# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@127.0.0.1:3306/user_management"
SQLALCHEMY_DATABASE_URL = os.getenv('MYSQLURLPATH')
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
