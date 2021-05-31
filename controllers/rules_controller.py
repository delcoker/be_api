import requests
import json
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import db

# Import os and dotenv to read data from env file
import os
from dotenv import load_dotenv

# custom
from core.models import users

class Rules:
    def __init__(self) -> None:
        print("welcome")
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
        print(json.dumps(response.json()))
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
        print(json.dumps(response.json()))


    # Code for setting the rules needed by twitter to start the fetch
    def set_rules(self):
        headers = self.create_headers(os.getenv('TWITTER_BEARER_TOKEN'))
        # get rules
        rules = self.get_rules(headers)
        # delete rules
        self.delete_all_rules(headers, rules)
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
            print(json.dumps(response.json()))

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