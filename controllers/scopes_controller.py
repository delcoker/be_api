# From system
from sqlalchemy.orm import Session

# Custom
from core.models.database import SessionLocal, engine, get
# from core.schemas import categories
from core.models import users
from controllers.crud import get_current_user

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Code for creating group category


def create_scope(db: Session, scope_name: str, scope: str, token: str):
    user = get_current_user(db, token)
    db_scope = users.Scope(
        user_id= user.id,
        name = scope_name,
        scope = scope
    )
    db.add(db_scope)
    db.commit()
    db.refresh(db_scope)
    return db_scope

# Get all Group Categories
def get_scopes(db: Session, token:str):
    user = get_current_user(db, token)
    return db.query(users.Scope).filter(users.Scope.user_id == user.id).all()

# Get a particular scope
def get_scope(db: Session, token: str, scope_id: int):
    user = get_current_user(db, token)
    return db.query(users.GroupCategory).filter(users.GroupCategory.id == group_category_id, users.GroupCategory.user_id == user.id).first()


def update_group_category(db: Session, group_category_id: int, group_category_name: str):
    result = db.query(users.GroupCategory).filter(users.GroupCategory.id == group_category_id).update({
        "group_category_name": group_category_name
    })
    db.commit()
    return result


def delete_group_category(db: Session, group_category_id: int):
    # get_current_user(db, token)
    result = db.query(users.GroupCategory).filter(users.GroupCategory.id == group_category_id).delete()
    db.commit()
    return result
