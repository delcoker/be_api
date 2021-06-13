import requests
import json
from fastapi_sqlalchemy import db

# Import os and dotenv to read data from env file
import os

# custom
from core.models import users


class Rules:
    def __init__(self) -> None:
        print("rules controller initialised")
        self.rules_uri = "https://api.twitter.com/2/tweets/search/stream/rules"

    # Code for creating headers to connect to twitter for the streams
    @staticmethod
    def create_headers(bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    # Get the rules that are stored by twitter for user account
    def get_rules(self, headers):
        response = requests.get(self.rules_uri, headers=headers)
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
        response = requests.post(self.rules_uri, headers=headers, json=payload)
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
            scope_map = self.match_similar_scope_to_multiple_users_and_sanitize_map(scopes)
            swap_scope_map = self.swap_key_values_dict(scope_map)
            sample_rules = []

            for user_ids, scopes_list in swap_scope_map.items():

                scope_concat = ''
                for scope in scopes_list:
                    if len(scope_concat + " OR " + scope) > 512 or len(scope_concat) - 4 > 512:  # if addition will be > than 512
                        if "OR" in scope_concat[:-4]:
                            scope_concat = scope_concat[:-4]
                        sample_rules.append({"value": scope_concat, "tag": user_ids})
                        scope_concat = ''
                    scope_concat += scope + " OR "

                sample_rules.append({"value": scope_concat[:-4], "tag": user_ids})

            payload = {"add": sample_rules}
            response = requests.post(self.rules_uri, headers=headers, json=payload)
            if response.status_code != 201:
                raise Exception(
                    "Cannot add rules (HTTP {}): {}".format(
                        response.status_code, response.text)
                )
            print(json.dumps(response.json()))

    @staticmethod
    def match_similar_scope_to_multiple_users_and_sanitize_map(scopes):
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

    @staticmethod
    def swap_key_values_dict(dictionary):
        new_dict = {}
        for key, value in dictionary.items():
            if value in new_dict:
                new_dict[value].append(key)
            else:
                new_dict[value] = [key]

        return new_dict
