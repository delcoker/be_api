# From system
import collections

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, text
import sqlalchemy as sa
import datetime
import json
import calendar
# from sqlalchemy.sql import text

# Custom
from core.models.database import SessionLocal, engine
from core.models import users


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def daily_collected_conversations(db: Session, start_date: str, end_date: str, granularity: str):
    # if granularity == 'month':
    #     monthly_conversations = db.query(extract('month',users.PostDataCategorisedView.created_at).label('months'), extract('year',users.PostDataCategorisedView.created_at).label('year'),func.count(users.PostDataCategorisedView.post_id).label('conversations') ).filter(
    #         users.PostDataCategorisedView.created_at >= start_date, users.PostDataCategorisedView.created_at <= end_date
    #     ).group_by(sa.func.month(users.PostDataCategorisedView.created_at)).all()
    #
    #     for month_ids, years, conversation_count in monthly_conversations:
    #         months.append(get_month_name(month_ids)+' '+str(years))
    #         conversation_counts.append(conversation_count)
    #
    #     monthly_sentiments = db.query(users.PostDataCategorisedView.sentiment_score, func.count(users.PostDataCategorisedView.post_id).label('conversations') ).filter(
    #         users.PostDataCategorisedView.created_at >= start_date, users.PostDataCategorisedView.created_at <= end_date
    #     ).group_by(users.PostDataCategorisedView.sentiment_score).all()

    # for sentiment_score, sentiment_count in monthly_sentiments:

    # elif granularity == 'year':

    # result = engine.execute(sql)
    # return result
    # names = [row[0] for row in result]
    # print(names)
    date_format, group_by = method_name(granularity)

    conversation_data = daily_conversations_chart(date_format, end_date, group_by, start_date)

    sentiment_data = positive_negative_chart(date_format, end_date, group_by, start_date)
    # there is sth wrong with this chart... not coming to mind now.. regarding the granularity

    charts = {"charts": [conversation_data, sentiment_data]}
    # charts = {"charts": [render_dict, render_dict]}
    return charts


def positive_negative_chart(date_format, end_date, group_by, start_date):
    dates = []
    positive_data = {}
    negative_data = {}
    positive_array_data = []
    negative_array_data = []
    sentiment_data = engine.execute(
        "SELECT DATE_FORMAT(created_at, '" + date_format + "') AS date, sentiment_score as 'sentiment', COUNT(post_id)  as 'count'" + \
        " FROM post_data_categorised_view WHERE created_at between '" + str(start_date) + "' and '" + str(
            end_date) + "' GROUP BY sentiment_score, " + group_by + " ORDER BY " + group_by + " DESC")

    for date, sentiment, count in sentiment_data:
        if date not in dates:
            dates.append(date)
        if sentiment == "POSITIVE":
            positive_data[date] = count
        elif sentiment == "NEGATIVE":
            negative_data[date] = count
    for date in dates:
        if date in positive_data:
            positive_array_data.append(positive_data[date])
        else:
            positive_array_data.append(None)

        if date in negative_data:
            negative_array_data.append(negative_data[date])
        else:
            negative_array_data.append(None)
        # positive_array_data.append(0) if date in positive_data else positive_array_data.append(positive_data[date])
        # negative_array_data.append(0) if date in negative_data else negative_array_data.append(negative_data[date])
    # return positive_array_data
    chart = {"type": 'column'}
    series = [{"name": 'positive', "data": positive_array_data}, {"name": 'negative', "data": negative_array_data}]
    title = {"text": 'My Title'}
    xAxis = {"categories": dates}

    sentiment_data = dict(id=2, chart=chart, series=series,
                          title=title, xAxis=xAxis)
    return sentiment_data


def daily_conversations_chart(date_format, end_date, group_by, start_date):
    categories = []
    data = []
    sql = "SELECT DATE_FORMAT(created_at, '" + date_format + "') AS date, COUNT(post_id) as 'Data' " + \
          "FROM post_data_categorised_view WHERE created_at between '" + str(start_date) + "' and '" + str(
        end_date) + "' GROUP BY " + group_by
    conversations_data = engine.execute(sql)

    for date, conversation_count in conversations_data:
        categories.append(date)
        data.append(conversation_count)

    chart = {"type": 'column'}
    series = [{"name": 'Daily Conversations', "data": data}]
    title = {"text": 'My Title'}
    xAxis = {"categories": categories}

    conversation_data = dict(id=1, chart=chart, series=series,
                             title=title, xAxis=xAxis)
    return conversation_data


def method_name(granularity):
    if granularity == 'year':
        date_format = '%Y'
        group_by = "YEAR(created_at)"
    elif granularity == 'month':
        date_format = '%M %Y'
        group_by = "MONTH(created_at), YEAR(created_at)"
    else:
        date_format = '%D %M %Y'
        group_by = "DAY(created_at), MONTH(created_at), YEAR(created_at)"
    return date_format, group_by


def get_month_name(month_number):
    return calendar.month_name[month_number]

# def create_chart():
