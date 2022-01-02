# From system
from sqlalchemy.orm import Session

# Custom
from auth import auth
from core.models.database import SessionLocal
from core.models import schema


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Code for creating group category
def create_group_category(db: Session, group_category_name: str, token: str):
    user = auth.get_user_token(db, token)
    db_group_category = schema.GroupCategory(
        user_id=user.id,
        group_category_name=group_category_name
    )
    db.add(db_group_category)
    db.commit()
    db.refresh(db_group_category)
    return db_group_category


# Get all Group Categories
def get_group_categories(db: Session, token: str):
    user = auth.get_user_token(db, token)
    # Limit and offset works like pagination
    return db.query(schema.GroupCategory) \
        .filter(schema.GroupCategory.user_id == user.id) \
        .all()


def get_group_category(db: Session, token: str, group_category_id: int):
    user = auth.get_user_token(db, token)
    return db.query(schema.GroupCategory) \
        .filter(schema.GroupCategory.id == group_category_id,
                schema.GroupCategory.user_id == user.id) \
        .first()


def update_group_category(db: Session, group_category_id: int, group_category_name: str, token: str):
    user = auth.get_user_token(db, token)
    result = db.query(schema.GroupCategory) \
        .filter(schema.GroupCategory.id == group_category_id,
                schema.GroupCategory.user_id == user.id) \
        .update({"group_category_name": group_category_name})
    db.commit()
    return result


def delete_group_category(db: Session, group_category_id: int, token: str):
    min_amount = 2
    auth.get_user_token(db, token)
    group_categories = get_group_categories(db, token)
    if len(group_categories) >= min_amount:
        result = db.query(schema.GroupCategory)\
            .filter(schema.GroupCategory.id == group_category_id)\
            .delete()
        db.commit()
        return result
    else:
        return min_amount
