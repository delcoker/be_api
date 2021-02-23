from sqlalchemy.orm import Session

from core.models import users
from core.schemas import user_schemas


def get_user(db: Session, user_id: int):
    return db.query(users.User).filter(users.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(users.User).filter(users.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(users.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: user_schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = users.User(
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        email=user.email, 
        password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
