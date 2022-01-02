# From system
from sqlalchemy.orm import Session

# Custom
# from controllers import rules_controller
from core.models.database import SessionLocal
from core.models import schema
# from controllers.crud import get_current_user

# from rules_controller import Rules
# rules = rules_controller.Rules()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Code for creating group category


# def create_scope(db: Session, scope: str, token: str):
#     user = get_current_user(db, token)
#     db_scope = users.Scope(
#         user_id=user.id,
#         scope=scope
#     )
#     db.add(db_scope)
#     db.commit()
#     db.refresh(db_scope)
#     rules.set_rules()
#     return db_scope
#
#
# # Get all Group Categories
# def get_scopes(db: Session, token: str):
#     user = get_current_user(db, token)
#     return db.query(users.Scope).filter(users.Scope.user_id == user.id).all()
#
#
# # Get a particular scope
# def get_scope(db: Session, token: str, scope_id: int):
#     user = get_current_user(db, token)
#     return db.query(users.Scope).filter(users.Scope.id == scope_id, users.Scope.user_id == user.id).first()
#

# Update a scope
def update_user(db: Session, user_id: int, f_name: str, l_name: str, phone: str):
    result = db.query(schema.User) \
        .filter(schema.User.id == user_id) \
        .update({"first_name": f_name,
                 "last_name": l_name,
                 "phone": phone})

    db.commit()
    return result

#
# # Delete a scope
# def delete_scope(db: Session, scope_id: int):
#     # get_current_user(db, token)
#     result = db.query(users.Scope).filter(users.Scope.id == scope_id).delete()
#     db.commit()
#     rules.set_rules()
#     return result
