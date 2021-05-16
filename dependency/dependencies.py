from core.models.database import SessionLocal, engine
from fastapi import Depends, HTTPException, status, Header
# Import JWT and authentication dependencies needed
from jose import JWTError, jwt
# Import os and dotenv to read data from env file
import os
from sqlalchemy.orm import Session

# Custom
from controllers import crud

#  Dependency for DB connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
# Connection fetch token and verify 
def get_user_token(db: Session=Depends(get_db), token: str = Header(...)):
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
        token_data = email
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data)
    if user is None:
        raise credentials_exception
    return user

