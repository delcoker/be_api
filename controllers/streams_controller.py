from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Test for stream
import requests
import json
import base64
# Test for stream end

from core.models.database import SessionLocal

# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# custom
from core.models import users
from controllers.crud import get_current_user

load_dotenv()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Code for generating bearer token
def generate_bearer_token():
    bearer_token = base64.b64encode(
        f"{os.getenv('TWITTER_CLIENT_ID')}:{os.getenv('TWITTER_CLIENT_SECRET')}".encode())
    headers = {
        "Authorization": f"Basic {bearer_token.decode()}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    resp = requests.post(
        url="https://api.twitter.com/oauth2/token",
        data={"grant_type": "client_credentials"},
        headers=headers,
    )
    data = resp.json()

    return data

# Code for creating headers to connect to twitter for the streams
def create_headers(bearer_token):
    # bearer_token = generate_bearer_token()
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

# Get the rules that are stored by twitter for user account
def get_rules(headers, bearer_token):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()

# Delete the rules stored by twitter for this user
def delete_all_rules(headers, bearer_token, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

# Code for setting the rules needed by twitter to start the fetch
def set_rules(headers, delete, bearer_token):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "#ecg"},
        {"value": "#esl"},
        {"value": "#dumsor"},
        {"value": "#fixthecountry"},
        {"value": "corona"},
        # {"value": "dog has:images", "tag": "dog pictures"},
        # {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    print(json.dumps(response.json()))

# Start getting tweets that contain the rules specified
def get_stream(headers, set, bearer_token,db): #, token:str
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?tweet.fields=attachments,author_id,created_at,entities,id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&expansions=author_id,geo.place_id&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type", headers=headers, stream=True,
        # "https://api.twitter.com/2/tweets/search/stream?tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld", headers=headers, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            # print(json.dumps(json_response, indent=4, sort_keys=True))
            # data = json.dumps(json_response, indent=4, sort_keys=True)
            print(json_response["data"])
            store_streams(json_response,db)

def store_streams(stream_results, db: Session): #, token: str, db: Session = Depends(get_db)
    # user = get_current_user(db, token)
    if hasattr(stream_results["includes"], "places"):
        geo_location = stream_results["includes"]["places"][0]["name"]
    else:
        geo_location = ''
    db_stream = users.Post(
        user_id = 1,
        data_id = stream_results["data"]["id"],
        data_author_id = stream_results["data"]["author_id"],
        data_user_name = stream_results["includes"]["users"][0]["username"],
        data_user_location = geo_location,
        text = stream_results["data"]["text"],
        full_object = json.dumps(stream_results, indent=4, sort_keys=True),
        created_at = stream_results["data"]["created_at"]
    )
#     db_stream = users.Post(
#     user_id = 1,
#     data_id = "429845243",
#     data_author_id = "347959834",
#     data_user_name = "skank",
#     data_user_location = '',
#     text = "rt @username kdfkemiofnew",
#     full_object = "jeifnweifgnweionfapiwefn",
#     created_at = "2021-05-19T10:10:58.000Z"
# )
    db.add(db_stream)
    db.commit()
    db.refresh(db_stream)