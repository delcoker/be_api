from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class PostDto(BaseModel):
    data_user_name: str
    source_name: str
    data_author_id: str
    data_user_location: str
    text: str
    country_name: Optional[str]
    state_name: Optional[str]
    city_name: Optional[str]
    created_at: datetime
    link: str
    sentiment: str = "str(999)"

    # link: Optional[str] = "None"

    # @classmethod
    # def linkk(useee):
    #     return useee

    class Config:
        orm_mode = True

#
# class PostCreate(PostBase):
#
#     class Config:
#         orm_mode = True
#
#
# class Post(PostCreate):
#     id: int
#     data_user_name: str
#     text: str
#
#     class Config:
#         orm_mode = True

# class PostDto(BaseModel):
#     __tablename__ = "posts"
#
#     source_name = Column(String, index=True)
#     data_author_id = Column(String, index=True)
#     data_user_name = Column(String, index=True)
#     data_user_location = Column(String, index=True)
#     text = Column(String, index=True)
#     country_name = Column(String, index=True)
#     state_name = Column(String, index=True)
#     city_name = Column(String, index=True)
#     created_at = Column(TIMESTAMP, index=True)
#
#     post_getter = relationship("User", back_populates="posts")
#     sentiment_scores = relationship("PostSentimentScore", back_populates="sentiment_post")
#
