from datetime import datetime

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from starlette.requests import Request

from auth import auth
from auth.auth import get_db
from controllers import graphs_controller

# Custom

router = APIRouter(
    prefix="/graphs",
    tags=["Graphs"],
    dependencies=[Depends(auth.get_user_from_token)]
)


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


@router.post("/map_locations")
def get_map_locations(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.ghana_locations_for_map(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/word_cloud/tweets")
def get_word_cloud_for_tweets(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.get_word_cloud_tweets(db, start_date, end_date, req.headers['token'])
    return graph_result


@router.post("/word_cloud/locations")
def get_word_cloud_for_keywords(req: Request, start_date: datetime = Form(...), end_date: datetime = Form(...), db: Session = Depends(get_db)):
    graph_result = graphs_controller.get_word_cloud_locations(db, start_date, end_date, req.headers['token'])
    return graph_result
