from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


# from core.models.schema import PostSentimentScore

# class PostSentimentScore(BaseModel):
#     sentiment_scores: List
#
#     class Config:
#         orm_mode = True


# from core.models import schema

# "sentiment_scores": [
#       {
#         "post_id": 323069,
#         "sentiment": "NEGATIVE",
#         "id": 119,
#         "score": -0.0895
#       }
#     ]


# def fo(f):
#     print("errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
#     return "rand"


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
    sentiment: str

    # sentiment_scores: List[PostSentimentScore] = None
    # sentiment_scores: PostSentimentScore

    # sentiment: BaseModel.schema(sentiment_scores)

    # link: Optional[str] = "None"

    # @classmethod
    # def linkk(useee):
    #     return useee

    class Config:
        orm_mode = True

#
# def those_things(any_variable: PostDto):
#     sentiment_scores = any_variable.sentiment_scores.sentiment
#     return sentiment_scores

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
#     post_user = relationship("User", back_populates="posts")
#     sentiment_scores = relationship("PostSentimentScore", back_populates="sentiment_post")
#
