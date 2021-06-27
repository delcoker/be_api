# From system

from sqlalchemy.orm import Session

# Custom
from core.models.database import SessionLocal, engine
from controllers.crud import get_current_user


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def daily_collected_conversations(db: Session, start_date: str, end_date: str, granularity: str, token: str):
    user = get_current_user(db, token)
    date_format, group_by_clause = get_date_granularity(granularity)

    conversation_data = daily_conversations_chart(date_format, start_date, end_date, group_by_clause, user)

    charts = {"charts": [conversation_data]}

    return charts


def positive_negative_conversations(db: Session, start_date: str, end_date: str, granularity: str, token: str):
    user = get_current_user(db, token)
    date_format, group_by_clause = get_date_granularity(granularity)

    sentiment_data = positive_negative_chart(date_format, start_date, end_date, group_by_clause, user)

    charts = {"charts": [sentiment_data]}

    return charts


def positive_negative_chart(date_format, start_date, end_date, group_by, user):
    dates = []
    positive_data = {}
    negative_data = {}
    neutral_dict = {}
    positive_array_data = []
    negative_array_data = []
    neutral_series_data = []
    sentiment_data = engine.execute(
        "SELECT DATE_FORMAT(created_at, '" + date_format + "') AS date, sentiment_score as 'sentiment', COUNT(post_id)  as 'count'" + \
        " FROM post_data_categorised_view WHERE user_id = " + str(user.id) + " AND created_at between '" + str(start_date) + "' and '" + str(
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

    chart = {"type": 'area', 'zoomType': 'xy'}
    series = [{"name": 'Positive', "data": positive_array_data},
              {"name": 'Negative', "data": negative_array_data},
              {"name": 'Neutral', "data": neutral_series_data}]
    title = {"text": 'Conversation Types'}
    xAxis = {"categories": dates}
    tooltip = get_tool_tip_format()
    plot_options = get_plot_options()
    exporting = {'enabled': True}

    sentiment_data = dict(id="collected_sentiments", chart=chart, series=series,
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


def daily_conversations_chart(date_format, start_date, end_date, group_by, user):
    categories = []
    data = []
    sql = "SELECT DATE_FORMAT(created_at, '{}') AS date, COUNT(post_id) as 'Data' " \
          "FROM post_data_categorised_view " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' " \
          "GROUP BY  + {}".format(date_format, user.id, start_date, end_date, group_by)

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

    conversation_data = dict(id="total_collected_conversations", chart=chart, series=series,
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


def highlights(db: Session, start_date, end_date, token: str):
    user = get_current_user(db, token)
    sql = "SELECT sentiment_score, COUNT(post_id) as count " \
          "FROM post_data_categorised_view " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' GROUP BY sentiment_score;".format(user.id, start_date, end_date)

    highlights_query = engine.execute(sql)

    sentiment_dict = {}
    for sentiment, count in highlights_query:
        sentiment_dict[sentiment] = count

    return sentiment_dict


def issue_of_importance(db: Session, start_date: str, end_date: str, token: str):
    user = get_current_user(db, token)

    issue_of_importance_data = issue_of_importance_chart(start_date, end_date, user)

    charts = {"charts": [issue_of_importance_data]}

    return charts


def issue_of_importance_chart(start_date, end_date, user):
    category_names = []
    importance = []
    sql = "SELECT categories.category_name, COUNT(post_id) as 'importance' " \
          "FROM post_data_categorised_view " \
          "JOIN categories ON post_data_categorised_view.category_id = categories.id " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' GROUP BY categories.category_name " \
          "ORDER BY importance DESC".format(user.id, start_date, end_date)

    issue_data = engine.execute(sql)

    for category_name, importance_data in issue_data:
        category_names.append(category_name)
        importance.append(importance_data)

    chart = {"type": 'bar', 'zoomType': 'xy'}
    series = [{"name": 'Importance', "data": importance}]
    title = {"text": 'Topic Importance'}
    xAxis = {"categories": category_names}
    plotOptions = get_plot_options()
    exporting = {'enabled': True}

    issue_of_importance_data = dict(id="issue_of_importance", chart=chart, series=series,
                                    title=title, xAxis=xAxis, plotOptions=plotOptions,
                                    exporting=exporting)

    return issue_of_importance_data


def issue_of_severity(db: Session, start_date: str, end_date: str, granularity: str, token: str):
    user = get_current_user(db, token)

    date_format, group_by_clause = get_date_granularity(granularity)

    issue_of_importance_data = issue_severity_chart(start_date, end_date, group_by_clause, user)

    charts = {"charts": [issue_of_importance_data]}

    return charts


def issue_severity_chart(start_date, end_date, group_by, user):
    categories_name = []
    positive_data = {}
    negative_data = {}
    neutral_dict = {}
    positive_array_data = []
    negative_array_data = []
    neutral_series_data = []

    sql = "SELECT categories.category_name, COUNT(post_id) as 'importance', sentiment_score " \
          "FROM post_data_categorised_view " \
          "JOIN categories ON post_data_categorised_view.category_id = categories.id " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' GROUP BY categories.category_name, sentiment_score " \
          "ORDER BY importance DESC".format(user.id, start_date, end_date)

    issue_severity_data = engine.execute(sql)

    for category_name, importance, sentiment_score in issue_severity_data:
        if category_name not in categories_name:
            categories_name.append(category_name)
        if sentiment_score == "POSITIVE":
            positive_data[category_name] = importance
        elif sentiment_score == "NEGATIVE":
            negative_data[category_name] = importance
        elif sentiment_score == "NEUTRAL":
            neutral_dict[category_name] = importance

    for category_name in categories_name:
        if category_name in positive_data:
            positive_array_data.append(positive_data[category_name])
        else:
            positive_array_data.append(0)

        if category_name in negative_data:
            negative_array_data.append(negative_data[category_name])
        else:
            negative_array_data.append(0)

        if category_name in neutral_dict:
            neutral_series_data.append(neutral_dict[category_name])
        else:
            neutral_series_data.append(0)

    chart = {"type": 'bar', 'zoomType': 'xy'}
    series = [{"name": 'Positive', "data": positive_array_data},
              {"name": 'Negative', "data": negative_array_data},
              {"name": 'Neutral', "data": neutral_series_data}]
    title = {"text": 'Topic Severity'}
    xAxis = {"categories": categories_name}
    tooltip = get_tool_tip_format()
    plot_options = get_plot_options()
    exporting = {'enabled': True}

    issue_severity_data_chart = dict(id="issue_of_severity", chart=chart, series=series,
                                     title=title, xAxis=xAxis, tooltip=tooltip, plotOptions=plot_options,
                                     exporting=exporting)
    return issue_severity_data_chart
