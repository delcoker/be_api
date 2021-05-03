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
    db_category = users.Category(
        group_category_id=category.group_category_id,
        category_name=category.category_name,
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Get a specific Category
def get_category(db: Session, category_id: int):
    return db.query(users.Category).filter(users.Category.id == category_id).first()
