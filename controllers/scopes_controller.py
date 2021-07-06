# From system
from sqlalchemy.orm import Session

# Custom
from controllers import rules_controller
from core.models.database import SessionLocal
from core.models import schema
from controllers.crud import get_current_user

# from rules_controller import Rules
test = rules_controller.Rules()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Code for creating group category
def create_scope(db: Session, scope: str, token: str):
    user = get_current_user(db, token)
    db_scope = schema.Scope(
        user_id=user.id,
        scope=scope
    )
    db.add(db_scope)
    db.commit()
    db.refresh(db_scope)
    test.set_rules()
    return db_scope


# Get all Group Categories
def get_scopes(db: Session, token: str):
    user = get_current_user(db, token)
    return db.query(schema.Scope).filter(schema.Scope.user_id == user.id).all()


# Get a particular scope
def get_scope(db: Session, token: str, scope_id: int):
    user = get_current_user(db, token)
    return db.query(schema.Scope).filter(schema.Scope.id == scope_id, schema.Scope.user_id == user.id).first()


# Update a scope
def update_scope(db: Session, scope_id: int, scope: str):
    bad_chars = [';', '"', "'", "*"]
    scope_list = scope.split(",")
    sanitized_list = []

    for stripped_string in scope_list:
        for i in bad_chars:
            stripped_string = stripped_string.replace(i, '')

        stripped_string = stripped_string.strip()
        if ' ' in stripped_string:
            stripped_string = '"' + stripped_string + '"'
        sanitized_list.append(stripped_string)

    # print(sanitized_list)
    scopes = ",".join(sanitized_list)

    result = db.query(schema.Scope).filter(schema.Scope.id == scope_id).update({
        "scope": scopes
    })
    db.commit()
    test.set_rules()
    return result


# Delete a scope
def delete_scope(db: Session, scope_id: int):
    # get_current_user(db, token)
    result = db.query(schema.Scope).filter(schema.Scope.id == scope_id).delete()
    db.commit()
    test.set_rules()
    return result
