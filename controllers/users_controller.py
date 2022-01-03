# From system
from sqlalchemy.orm import Session

from auth import auth
from core.models import schema


def create_user(db: Session, first_name: str, last_name: str, email: str, phone: str, password: str):
    db_user = schema.User(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        password=auth.get_password_hash(password))

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_group_category = schema.GroupCategory(
        user_id=db_user.id,
        group_category_name="Topics")

    db.add(db_group_category)
    db.commit()
    db.refresh(db_group_category)
    return db_user


# Update a user
def update_user(db: Session, user_id: int, f_name: str, l_name: str, phone: str):
    result = db.query(schema.User) \
        .filter(schema.User.id == user_id) \
        .update({"first_name": f_name,
                 "last_name": l_name,
                 "phone": phone})
    db.commit()
    return result


def get_user(db: Session, user_id: int):
    # return db.query(users.User).filter(users.User.id == user_id).first()
    return db.query(schema.User) \
        .filter(schema.User.id == user_id) \
        .first()


def get_users(db: Session):  # , skip: int = 0, limit: int = 100
    # Limit and offset works like pagination
    # return db.query(users.User).offset(skip).limit(limit).all()
    return db.query(schema.User).all()


def get_user_by_email(db: Session, email: str):
    return db.query(schema.User) \
        .filter(schema.User.email == email) \
        .first()
