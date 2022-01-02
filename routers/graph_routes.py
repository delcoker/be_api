from datetime import datetime

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from starlette.requests import Request

from controllers import crud, graphs_controller
# Custom
from core.models.database import SessionLocal

router = APIRouter(
    prefix="/graphs",
    tags=["Graphs"],
    dependencies=[Depends(crud.get_user_token)]
)


#  Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/collected_conversations")
def get_graphs(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), granularity: str = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.daily_collected_conversations(db, start_date, end_date, granularity, req.headers['token'])
    return graph_result


@router.post("/collected_sentiment_types")
def get_graphs(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), granularity: str = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.positive_negative_conversations(db, start_date, end_date, granularity, req.headers['token'])
    return graph_result


@router.post("/highlights")
def get_highlights(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.highlights(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/issue_importance")
def get_issue_of_importance_chart(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.issue_of_importance(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/issue_severity")
def get_issue_of_severity_chart(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.issue_of_severity(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/locations")
def get_locations_chart(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.ghana_locations(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/word_cloud/tweets")
def get_word_cloud_for_tweets(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.get_word_cloud_for_tweets(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/word_cloud/locations")
def get_word_cloud_for_keywords(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.get_word_cloud_for_locations(db, start_date, end_date, req.headers['token'])
    return graph_result
