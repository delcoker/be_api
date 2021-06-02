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
from controllers.rules_controller import Rules

load_dotenv()


# MyTwitter is inheriting from the parent class 'Rules' found in rules controller
class MyTwitter(Rules):

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
        super().__init__()
        # Start queues for streams and sentiment scores
        self.stream_queue = Queue()
        self.sentiment_queue = Queue()

        # Threads so functions can be running in background asynchronously
        threading.Thread(target=self.store_streams, daemon=True).start()
        threading.Thread(target=self.score_sentiment, daemon=True).start()

        # create headers
        headers = self.create_headers(os.getenv('TWITTER_BEARER_TOKEN'))
        # get rules
        # rules = self.get_rules(headers)
        # delete rules
        # self.delete_all_rules(headers, rules)
        # set rules is being called from the rules controller
        self.set_rules()
        # start stream
        self.get_stream(headers)

    # Start getting tweets that contain the rules specified
    def get_stream(self, headers):  # , token:str set, bearer_token,
        print("getting streams method")
        count = 1
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
                        count = 1
            except Exception as r:
                # if response.status_code == 429:
                print(' Put to sleep before retrying.')
                time_count = 180 * count
                time.sleep(time_count)
                count += 1
                # print(r)
                print("Printed after " + str(time_count) + " seconds.")
                # print("Printed after 5 seconds.")
                continue
                # else:
                #     print(' Put to sleep before retrying.')
                #     time.sleep(5)
                #     print("Printed after 5 seconds.")

    def score_sentiment(self):
        print("score sentiment method")
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
        print("store streams method")
        while True:
            stream_results = self.stream_queue.get()
            # print(stream_results)
            if stream_results:
                # check for geo location if it exists
                geo_location = ''
                try:
                    if hasattr(stream_results["includes"], "places"):
                        geo_location = stream_results["includes"]["places"][0]["name"]
                        print("has geo:", geo_location)
                except Exception as e:
                    continue

                # Split user ids that are returned from twitter
                # if hasattr(stream_results, 'matching_rules'):
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
