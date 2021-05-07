# From system
from sqlalchemy.orm import Session

# Custom
from core.models.database import SessionLocal, engine
from core.schemas import categories
from core.models import users

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get all Categories
def get_all_categories(db: Session):
    # Limit and offset works like pagination
    return db.query(users.Category).all()

# Get all Group Categories
def create_category(db: Session, category: categories.CategoryCreate):
    category_data = category.dict()
    keyword_data = category_data.pop('keywords')
    db_category = users.Category(**category_data)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    category_id = db_category.id

    if keyword_data:
        for keyword in keyword_data:
            # get category id
            keyword['category_id'] = category_id
            db_keywords = users.Keyword(**keyword)
            db.add(db_keywords)
            db.commit()
            db.refresh(db_keywords)
    return db_category

# Get a specific Category
def get_category(db: Session, category_id: int):
    return db.query(users.Category).filter(users.Category.id == category_id).first()

# Update a particular category
def update_category(db: Session, category_id: int, category: categories.CategoryCreate):
    category_data = category.dict()
    keyword_data = category_data.pop('keywords')
    result = db.query(users.Category).filter(users.Category.id == category_id).update({
        "group_category_id": category_data['group_category_id'],
        "category_name": category_data['category_name']
    })
    db.commit()
    if keyword_data:
        for keyword in keyword_data:
            # get category id
            keyword['category_id'] = category_id
            db.query(users.Keyword).filter(users.Keyword.id == keyword['id']).update({
                "keywords": keyword['keywords']
            })
        db.commit()
    return result

# Delete a particular category
def delete_category(db: Session, category_id: int):
    result = db.query(users.Category).filter(
        users.Category.id == category_id).delete()
    db.commit()
    return result
