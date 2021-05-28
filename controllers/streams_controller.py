# System Imports
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import db

# Test for stream
import requests
import json
import base64
# Test for stream end

from core.models.database import SessionLocal, engine

# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# custom
from core.models import users
from controllers.crud import get_current_user
from queue import Queue
import threading
from dependency.vader_sentiment_api import SentimentApi
from requests.exceptions import ProxyError, Timeout, ConnectionError, ChunkedEncodingError
import time

load_dotenv()


class MyTwitter:

    # Code for generating bearer token
    def generate_bearer_token(self):
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

    def __init__(self) -> None:
        # Start queues for streams and sentiment scores
        self.stream_queue = Queue()
        self.sentiment_queue = Queue()

        # Threads so functions can be running in background asynchronously
        threading.Thread(target=self.store_streams, daemon=True).start()
        threading.Thread(target=self.score_sentiment, daemon=True).start()

        # create headers
        headers = self.create_headers(os.getenv('BEARER_TOKEN_SHAMIR'))
        # get rules
        rules = self.get_rules(headers)
        # delete rules
        self.delete_all_rules(headers, rules)
        # set rules
        self.set_rules(headers)
        # start stream
        self.get_stream(headers)

    # Code for creating headers to connect to twitter for the streams
    def create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    # Get the rules that are stored by twitter for user account
    def get_rules(self, headers):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules", headers=headers
        )
        if response.status_code != 200:
            raise Exception(
                "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
            )
        # print(json.dumps(response.json()))
        return response.json()

    def delete_all_rules(self, headers, rules):
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
        # print(json.dumps(response.json()))

    # Code for setting the rules needed by twitter to start the fetch
    def set_rules(self, headers):
        with db():
            scopes = db.session.query(users.Scope).all()
            # Put scopes in map to group users with same scopes
            scope_map = self.get_scopes_map(scopes)
            sample_rules = []
            for scope, user_ids in scope_map.items():
                sample_rules.append({"value": scope, "tag": user_ids})
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
            # print(json.dumps(response.json()))

    def get_scopes_map(self, scopes):
        scope_map = {}
        for scope_row in scopes:
            scopes_obj = scope_row.scope.split(',')  # split scopes
            for scope in scopes_obj:
                sanitized_scope = scope.strip()  # strip any leading or trailing whitespaces
                if sanitized_scope in scope_map:
                    scope_map[sanitized_scope] = scope_map[sanitized_scope] + "," + str(
                        scope_row.user_id)  # if map has scope just concat user
                    # print(scope_map[sanitized_scope])
                else:
                    scope_map[sanitized_scope] = str(
                        scope_row.user_id)  # else create an index for the scope with the user id
        return scope_map  # return scope map

    # Start getting tweets that contain the rules specified
    def get_stream(self, headers):  # , token:str set, bearer_token,
        # print("getting streams method")
        count = 120
        while True:
            response = requests.get(
                "https://api.twitter.com/2/tweets/search/stream?tweet.fields=attachments,author_id,created_at,entities,id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&expansions=author_id,geo.place_id&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type",
                headers=headers, stream=True,
            )
            try:
                for response_line in response.iter_lines():
                    if response_line:
                        json_response = json.loads(response_line)
                        self.stream_queue.put(json_response)
                        count = 120
            except Exception:
                # if response.status_code == 429:
                time.sleep(count)
                count *= count
                # else:
                #     print(' Put to sleep before retrying.')
                #     time.sleep(5)
                #     print("Printed after 5 seconds.")
                continue

    def score_sentiment(self):
        # print("score sentiment method")
        while True:
            post_to_score = self.sentiment_queue.get()
            if post_to_score:
                # print(f"Scoring {post_to_score.id}")
                result = SentimentApi().getSentiment(str(post_to_score.text))

                db_sentiment = users.PostSentimentScore(
                    post_id=post_to_score.id,
                    sentiment=result["sentiment"],
                    score=result["score"]
                )
                try:
                    with db():
                        db.session.add(db_sentiment)
                        db.session.commit()
                        db.session.refresh(db_sentiment)
                except Exception as e:
                    # print("NOT saved")
                    print(e)
                # print(f"Scored {post_to_score.id}")

    def store_streams(self):  # , token: str, db: Session = Depends(get_db)
        # print("store streams method")
        while True:
            stream_results = self.stream_queue.get()
            # print(stream_results)
            if stream_results:
                # check for geo location if it exists
                if hasattr(stream_results["includes"], "places"):
                    geo_location = stream_results["includes"]["places"][0]["name"]
                else:
                    geo_location = ''
                # Split user ids that are returned from twitter
                user_ids = stream_results['matching_rules'][0]["tag"].split(",")
                for user_id in user_ids:
                    db_stream = users.Post(
                        user_id=user_id,
                        source_name="twitter",
                        data_id=stream_results["data"]["id"],
                        data_author_id=stream_results["data"]["author_id"],
                        data_user_name=stream_results["includes"]["users"][0]["username"],
                        data_user_location=geo_location,
                        text=stream_results["data"]["text"],
                        full_object=json.dumps(stream_results, indent=4, sort_keys=True),
                        created_at=stream_results["data"]["created_at"]
                    )
                    try:
                        with db():
                            db.session.add(db_stream)
                            db.session.commit()
                            db.session.refresh(db_stream)
                            self.sentiment_queue.put(db_stream)
                    except Exception as e:
                        # print("NOT saved")
                        print(e)
