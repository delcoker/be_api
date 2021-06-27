from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
# Custom
from core.models.database import SessionLocal
from dependency.dependencies import get_user_token
from controllers import crud, graphs_controller

router = APIRouter(
    prefix="/graphs",
    tags=["Graphs"],
    # dependencies=[Depends(get_user_token)]
)


#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/collected_conversations")
def get_graphs(start_date: datetime = Form(...), end_date: datetime = Form(...), granularity: str = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.daily_collected_conversations(db, start_date, end_date, granularity)
    return graph_result


@router.post("/collected_sentiment_types")
def get_graphs(start_date: datetime = Form(...), end_date: datetime = Form(...), granularity: str = Form(...)):
    graph_result = graphs_controller.positive_negative_conversations(start_date, end_date, granularity)
    return graph_result


@router.post("/highlights")
def get_highlights(start_date: datetime = Form(...), end_date: datetime = Form(...)):
    graph_result = graphs_controller.highlights(start_date, end_date)
    return graph_result
