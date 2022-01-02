# From system

from sqlalchemy.orm import Session

# Custom
import stop_words_custom
from controllers import crud
from core.models.database import SessionLocal, engine
import re
import statistics

import stop_words


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


view_in_use = 'post_data_categorised_view'


def daily_collected_conversations(db: Session, start_date: str, end_date: str, granularity: str, token: str):
    user = crud.get_user_token(db, token)
    date_format, group_by_clause = get_date_granularity(granularity)

    conversation_data = daily_conversations_chart(date_format, start_date, end_date, group_by_clause, user)

    charts = {"charts": [conversation_data]}

    return charts


def positive_negative_conversations(db: Session, start_date: str, end_date: str, granularity: str, token: str):
    user = crud.get_user_token(db, token)
    date_format, group_by_clause = get_date_granularity(granularity)

    sentiment_data = positive_negative_chart(date_format, start_date, end_date, group_by_clause, user)

    charts = {"charts": [sentiment_data]}

    return charts


def positive_negative_chart(date_format, start_date, end_date, group_by_clause, user):
    dates = []
    positive_data = {}
    negative_data = {}
    neutral_dict = {}
    positive_array_data = []
    negative_array_data = []
    neutral_series_data = []

    sql = "SELECT {} AS date, sentiment_score as 'sentiment', COUNT(post_id) as 'count' " \
          "FROM {} " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' " \
          "GROUP BY {}, sentiment_score".format(date_format, view_in_use, user.id, start_date, end_date, group_by_clause)

    sentiment_data = engine.execute(sql)

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

    chart = {"type": 'area', 'zoomType': 'xy', 'height': 400}
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
                'enabled': True
            },
            'dataLabels': {
                'enabled': True,
            }
        },
        'area': {
            'dataLabels': {
                'enabled': False,
            }
        },
        # "bar": {
        #     "stacking": "percent"
        # }
    }


def get_stacked_bar_plot_options():
    return {
        'series': {
            'marker': {
                'enabled': True
            }
        },
        'line': {
            'marker': {
                'enabled': True
            }
        },
        "bar": {
            "stacking": "percent",
            'dataLabels': {
                'enabled': True,
                'format': '{point.percentage:.0f}%'
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


def daily_conversations_chart(date_format, start_date, end_date, group_by_clause, user):
    categories = []
    data = []
    sql = "SELECT {} AS date, COUNT(post_id) as 'data' " \
          "FROM {} " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' " \
          "GROUP BY {}".format(date_format, view_in_use, user.id, start_date, end_date, group_by_clause)

    conversations_data = engine.execute(sql)

    for date, conversation_count in conversations_data:
        categories.append(date)
        data.append(conversation_count)

    chart = {"type": 'spline', 'zoomType': 'xy', 'height': 400}
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
        date_format = 'DATE_FORMAT(created_at, "%Y")'
        group_by = "YEAR(created_at)"
    elif granularity == 'month':
        date_format = 'DATE_FORMAT(created_at, "%b %Y")'
        group_by = "YEAR(created_at), MONTH(created_at)"
    elif granularity == 'day':
        date_format = 'DATE_FORMAT(created_at, "%d %b %Y")'
        group_by = "YEAR(created_at), MONTH(created_at), DAY(created_at)"
    else:
        date_format = "(CONCAT('Week ',WEEK(created_at, 3) - WEEK(created_at - INTERVAL DAY(created_at) - 1 DAY, 3) + 1, ' ', DATE_FORMAT(created_at, '%b %Y')))"
        group_by = " YEAR(created_at), MONTH(created_at), date"

    return date_format, group_by


def highlights(db: Session, start_date, end_date, token: str):
    user = crud.get_user_token(db, token)
    sql = "SELECT sentiment_score, COUNT(post_id) as count " \
          "FROM {} " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' " \
          "GROUP BY sentiment_score;".format(view_in_use, user.id, start_date, end_date)

    highlights_query = engine.execute(sql)

    sentiment_dict = {}
    for sentiment, count in highlights_query:
        sentiment_dict[sentiment] = count

    return sentiment_dict


def issue_of_importance(db: Session, start_date: str, end_date: str, token: str):
    user = crud.get_user_token(db, token)

    issue_of_importance_data = issue_of_importance_chart(start_date, end_date, user)

    charts = {"charts": [issue_of_importance_data]}

    return charts


def issue_of_importance_chart(start_date, end_date, user):
    category_names = []
    importance = []
    sql = "SELECT categories.category_name, COUNT(post_id) as 'importance' " \
          "FROM {} " \
          "JOIN categories ON {}.category_id = categories.id " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' " \
          "GROUP BY categories.category_name " \
          "ORDER BY importance DESC".format(view_in_use, view_in_use, user.id, start_date, end_date)

    issue_data = engine.execute(sql)

    for category_name, importance_data in issue_data:
        category_names.append(category_name)
        importance.append(importance_data)

    chart = {"type": 'bar', 'zoomType': 'xy', 'height': 700}
    series = [{"name": 'Importance', "data": importance}]
    title = {"text": 'Topic Importance'}
    xAxis = {"categories": category_names}
    plotOptions = get_plot_options()
    exporting = {'enabled': True}

    issue_of_importance_data = dict(id="issue_of_importance", chart=chart, series=series,
                                    title=title, xAxis=xAxis, plotOptions=plotOptions,
                                    exporting=exporting)

    return issue_of_importance_data


def issue_of_severity(db: Session, start_date: str, end_date: str, token: str):
    user = crud.get_user_token(db, token)

    issue_of_importance_data = issue_severity_chart(start_date, end_date, user)

    charts = {"charts": [issue_of_importance_data]}

    return charts


def issue_severity_chart(start_date, end_date, user):
    categories_name = []
    positive_data = {}
    negative_data = {}
    neutral_dict = {}
    positive_array_data = []
    negative_array_data = []
    neutral_series_data = []

    sql = "SELECT categories.category_name, COUNT(post_id) as 'importance', sentiment_score " \
          "FROM {} " \
          "JOIN categories ON {}.category_id = categories.id " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' " \
          "GROUP BY categories.category_name, sentiment_score " \
          "ORDER BY importance DESC".format(view_in_use, view_in_use, user.id, start_date, end_date)

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
            positive_array_data.append(None)

        if category_name in negative_data:
            negative_array_data.append(negative_data[category_name])
        else:
            negative_array_data.append(None)

        if category_name in neutral_dict:
            neutral_series_data.append(neutral_dict[category_name])
        else:
            neutral_series_data.append(None)

    chart = {"type": 'bar', 'zoomType': 'xy', 'height': 700}
    series = [{"name": 'Positive', "data": positive_array_data},
              {"name": 'Negative', "data": negative_array_data},
              {"name": 'Neutral', "data": neutral_series_data}]
    title = {"text": 'Topic Severity'}
    xAxis = {"categories": categories_name}
    tooltip = get_tool_tip_format()
    plot_options = get_stacked_bar_plot_options()
    exporting = {'enabled': True}

    issue_severity_data_chart = dict(id="issue_of_severity", chart=chart, series=series,
                                     title=title, xAxis=xAxis, tooltip=tooltip, plotOptions=plot_options,
                                     exporting=exporting)
    return issue_severity_data_chart


def ghana_locations(db: Session, start_date, end_date, token: str):  # not tested
    user = crud.get_user_token(db, token)
    country = "AND country = 'ghana'"
    country = ""
    categories_name = []
    positive_data = {}
    negative_data = {}
    neutral_dict = {}
    positive_array_data = []
    negative_array_data = []
    neutral_series_data = []

    sql = "SELECT categories.category_name, state, city, COUNT(city) as 'city_count' " \
          "FROM {} " \
          "JOIN categories ON {}.category_id = categories.id " \
          "WHERE user_id = {} AND created_at between '{}' AND '{}' {}" \
          "GROUP BY categories.category_name, city, 'city_count';".format(view_in_use, view_in_use, user.id, start_date, end_date, country)

    locations = engine.execute(sql)

    for category_name, importance, sentiment_score in locations:
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
    title = {"text": 'Location'}
    xAxis = {"categories": categories_name}
    tooltip = get_tool_tip_format()
    plot_options = get_stacked_bar_plot_options()
    exporting = {'enabled': True}

    locations_chart = dict(id="issue_of_severity", chart=chart, series=series,
                           title=title, xAxis=xAxis, tooltip=tooltip, plotOptions=plot_options,
                           exporting=exporting)
    return locations_chart


def get_word_cloud_for_tweets(db: Session, start_date: str, end_date: str, token: str):
    user = crud.get_user_token(db, token)

    sql = "SELECT text " \
          "FROM {} " \
          "WHERE user_id = {} AND created_at between '{}' and '{}' ".format(view_in_use, user.id, start_date, end_date)

    tweet_data = engine.execute(sql)

    frequencies = {}

    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    regex = "^[A-Za-z0-9_-]*$"

    for text in tweet_data:
        word_array_dirty = str(text.text).split()
        word_array = []

        for word in word_array_dirty:
            if len(word.strip()) > 3 and word.strip() not in stop_words.stop_words and re.search(regex, word):
                word_array.append(word.lower())

        for word in word_array:
            if word in frequencies:
                frequencies[word] = frequencies[word] + 1
            else:
                frequencies[word] = 1

    frequency_values = frequencies.values()

    if len(frequency_values) < 1:
        return [{'text': "Nothing", 'value': 100, },
                {'text': "here", 'value': 75, },
                {'text': "yet", 'value': 59, },
                {'text': "so", 'value': 100, },
                {'text': "chill", 'value': 111, },
                {'text': "ha ha ha", 'value': 20, },
                ]

    frequency_median = statistics.median(frequency_values)
    frequency_mode = statistics.mode(frequency_values)
    frequency_mean = statistics.mode(frequency_values)

    frequency_threshold = frequency_median
    if frequency_mode > frequency_threshold:  # not sure if mode should be used
        frequency_threshold = frequency_mode
    if frequency_mean > frequency_threshold:
        frequency_threshold = frequency_mean

    frequency_threshold = statistics.mean([val for val in frequency_values if val > frequency_threshold])

    return {
        'title': 'tweet words',
        'value': [{'text': k, 'value': v} for (k, v) in frequencies.items() if v > frequency_threshold]
    }


def get_word_cloud_for_locations(db: Session, start_date: str, end_date: str, token: str):
    user = crud.get_user_token(db, token)

    sql = "SELECT state, city " \
          "FROM {} " \
          "WHERE user_id = {} " \
          "AND (state <> '' or city <> '') " \
          'AND country = "ghana" ' \
          "AND created_at BETWEEN '{}' AND '{}' ".format(view_in_use, user.id, start_date, end_date)

    tweet_data = engine.execute(sql)

    frequencies = {}

    regex = "^[A-Za-z0-9_-]*$"

    all_stop_words = stop_words.stop_words + stop_words_custom.stop_words

    for data in tweet_data:
        word_state = data.state.decode()
        word_city = data.city.decode()
        word_array_dirty = [str(word_state)] + [str(word_city)]
        word_array = []

        for word in word_array_dirty:
            if len(word.strip()) > 3 and word.strip() not in all_stop_words:  # and re.search(regex, word):
                word_array.append(word.lower())

        for word in word_array:
            if word in frequencies:
                frequencies[word] = frequencies[word] + 1
            else:
                frequencies[word] = 1

    frequency_values = frequencies.values()

    if len(frequency_values) < 1:
        return [{'text': "Nothing", 'value': 100, },
                {'text': "here", 'value': 75, },
                {'text': "yet", 'value': 59, },
                {'text': "so", 'value': 100, },
                {'text': "chill", 'value': 111, },
                {'text': "ha ha ha", 'value': 20, },
                ]

    return {'title': '🇬🇭 .gh locations',
            'value': [{'text': k, 'value': v} for (k, v) in frequencies.items()]}

# def get_word_cloud_for_keywords(db: Session, start_date: str, end_date: str): #, token: str
#     # user = get_current_user(db, token)
#     sql = "SELECT text " \
#           "FROM post_data_categorised_view " \
#           "WHERE user_id = {} AND created_at between '{}' and '{}' ".format(1, start_date, end_date)
#     sql_data = []
#     frequencies = {}
