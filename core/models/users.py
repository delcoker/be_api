from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    password = Column(String)

    # These are links to the other tables so this table can fetch data from the other tables and thos tables 
    # can fetch data from this table. it does this via the foreign key join
    social_accounts = relationship("SocialAccount", back_populates="owner", cascade="all, delete", passive_deletes=True)  # so oncascade it should delete the data in other tables that are linked to it
    group_categories = relationship("GroupCategory", back_populates="owner_of_group_category", cascade="all, delete", passive_deletes=True)
    scopes = relationship("Scope", back_populates="creator", cascade="all, delete", passive_deletes=True)

class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    oauth_token = Column(String, index=True)
    oauth_token_secret = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("User", back_populates="social_accounts")

class GroupCategory(Base):
    __tablename__ = "group_categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    group_category_name = Column(String, index=True)

    owner_of_group_category = relationship("User", back_populates="group_categories")
    categories = relationship("Category", back_populates="group_category")
    

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    group_category_id = Column(Integer, ForeignKey('group_categories.id'))
    category_name = Column(String, index=True)

    group_category = relationship("GroupCategory", back_populates="categories")
    keywords = relationship("Keyword", back_populates="category")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer,  ForeignKey('categories.id'))
    keywords = Column(String, index=True)

    category = relationship("Category", back_populates="keywords")

class Scope(Base):
    __tablename__ = "scopes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,  ForeignKey('users.id'))
    scope = Column(String, index=True)

    creator = relationship("User", back_populates="scopes")
