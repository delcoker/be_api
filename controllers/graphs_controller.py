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
    #     ).group_by_clause(sa.func.month(users.PostDataCategorisedView.created_at)).all()
    #
    #     for month_ids, years, conversation_count in monthly_conversations:
    #         months.append(get_month_name(month_ids)+' '+str(years))
    #         conversation_counts.append(conversation_count)
    #
    #     monthly_sentiments = db.query(users.PostDataCategorisedView.sentiment_score, func.count(users.PostDataCategorisedView.post_id).label('conversations') ).filter(
    #         users.PostDataCategorisedView.created_at >= start_date, users.PostDataCategorisedView.created_at <= end_date
    #     ).group_by_clause(users.PostDataCategorisedView.sentiment_score).all()

    # for sentiment_score, sentiment_count in monthly_sentiments:

    # elif granularity == 'year':

    # result = engine.execute(sql)
    # return result
    # names = [row[0] for row in result]
    # print(names)

    date_format, group_by_clause = get_date_granularity(granularity)

    conversation_data = daily_conversations_chart(date_format, start_date, end_date, group_by_clause)

    charts = {"charts": [conversation_data]}
    # charts = {"charts": [render_dict, render_dict]}
    return charts


def positive_negative_conversations(start_date: str, end_date: str, granularity: str):
    date_format, group_by_clause = get_date_granularity(granularity)

    sentiment_data = positive_negative_chart(date_format, start_date, end_date, group_by_clause)

    charts = {"charts": [sentiment_data]}

    return charts


def positive_negative_chart(date_format, start_date, end_date, group_by):
    dates = []
    positive_data = {}
    negative_data = {}
    neutral_dict = {}
    positive_array_data = []
    negative_array_data = []
    neutral_series_data = []
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
        elif sentiment == "NEUTRAL":
            neutral_dict[date] = count
    for date in dates:
        if date in positive_data:
            positive_array_data.append(positive_data[date])
        else:
            positive_array_data.append(0)

        if date in negative_data:
            negative_array_data.append(negative_data[date])
        else:
            negative_array_data.append(0)

        if date in neutral_dict:
            neutral_series_data.append(neutral_dict[date])
        else:
            neutral_series_data.append(0)
        # positive_array_data.append(0) if date in positive_data else positive_array_data.append(positive_data[date])
        # negative_array_data.append(0) if date in negative_data else negative_array_data.append(negative_data[date])
    # return positive_array_data

    chart = {"type": 'area', 'zoomType': 'xy'}
    series = [{"name": 'Positive', "data": positive_array_data},
              {"name": 'Negative', "data": negative_array_data},
              {"name": 'Neutral', "data": neutral_series_data}]
    title = {"text": 'Conversation Types'}
    xAxis = {"categories": dates}
    tooltip = get_tool_tip_format()
    plot_options = get_plot_options()
    exporting = {'enabled': True}

    sentiment_data = dict(id="total_conversations", chart=chart, series=series,
                          title=title, xAxis=xAxis, tooltip=tooltip, plotOptions=plot_options,
                          exporting=exporting)
    return sentiment_data


def get_plot_options():
    return {
        'series': {
            'marker': {
                'enabled': False
            }
        },
        'line': {
            'marker': {
                'enabled': True
            }
        }
    }


def get_tool_tip_format():
    return {
        "headerFormat": '<span style="font-size:10px">{point.key}</span><table>',
        "pointFormat": '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                       '<td style="padding:0"><b>{point.y:.0f}</b></td></tr>',
        "footerFormat": '</table>',
        "shared": True,
        "useHTML": True
    }


def daily_conversations_chart(date_format, start_date, end_date, group_by):
    categories = []
    data = []
    sql = "SELECT DATE_FORMAT(created_at, '{}') AS date, COUNT(post_id) as 'Data' " \
          "FROM post_data_categorised_view " \
          "WHERE created_at between '{}' and '{}' " \
          "GROUP BY  + {}".format(date_format, start_date, end_date, group_by)

    conversations_data = engine.execute(sql)

    for date, conversation_count in conversations_data:
        categories.append(date)
        data.append(conversation_count)

    chart = {"type": 'spline', 'zoomType': 'xy'}
    series = [{"name": 'Total Conversations', "data": data}]
    title = {"text": 'Total Conversations'}
    xAxis = {"categories": categories}
    plotOptions = get_plot_options()
    exporting = {'enabled': True}

    conversation_data = dict(id=1, chart=chart, series=series,
                             title=title, xAxis=xAxis, plotOptions=plotOptions,
                             exporting=exporting)
    return conversation_data


def get_date_granularity(granularity):
    if granularity == 'year':
        date_format = '%Y'
        group_by = "YEAR(created_at)"
    elif granularity == 'month':
        date_format = '%b %Y'
        group_by = "MONTH(created_at), YEAR(created_at)"
    else:
        date_format = '%d %b %Y'
        group_by = "DAY(created_at), MONTH(created_at), YEAR(created_at)"

    return date_format, group_by


def get_month_name(month_number):
    return calendar.month_name[month_number]


def highlights(start_date, end_date):
    sql = "SELECT sentiment_score, COUNT(post_id) as count " \
          "FROM post_data_categorised_view " \
          "WHERE created_at between '{}' and '{}' GROUP BY sentiment_score;".format(start_date, end_date)

    highlights_query = engine.execute(sql)

    sentiment_dict = {}
    for sentiment, count in highlights_query:
        sentiment_dict[sentiment] = count

    return sentiment_dict
