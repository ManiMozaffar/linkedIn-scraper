import re

import requests

from services.common import RedisCrud
from services.tech.factory import KeyWordCrud


class TelegramCrud(RedisCrud):
    @property
    def get_context(self):
        return list(self.get(["keywords"]))

    def get_user_expression(self, user_id: int):
        result = self.get([user_id])
        return None if len(result) == 0 else result.pop()

    def eval(self, context, user_expression, ads_keywords) -> dict:
        payload = {
            "context": context,
            "expression": user_expression,
            "filter": ads_keywords
        }
        resp = requests.Session().post("http://isolated:9999", json=payload)
        return resp.json()

    def update_user_expression(
            self, user_id, context, user_expression, ads_keywords,
            regex=r'\b(?!\band\b|\bor\b)\w+\b'
    ):
        old_expression = self.get_user_expression(user_id)
        if old_expression:
            for namespace in set(re.findall(regex, old_expression)):
                print(namespace, [user_id])
                self.delete(namespace, [user_id])

        resp = self.eval(
            context, user_expression, ads_keywords
        )
        if resp.get("success"):
            self.reset_and_add(user_id, [user_expression])
            for namespace in resp.get("namespaces"):
                self.add(namespace, [user_id, ])
        return resp


class TelegramRetriever(TelegramCrud, KeyWordCrud):
    def get_all_active_users(self):
        result = self.get(["all_users"])
        if not result:
            ads_keywords = self.get_all_keywords()
            all_related_users = self.union_related_user_tech(ads_keywords)
            self.add("all_users", all_related_users, ex=3600)
            return all_related_users
        else:
            return result

    def get_all_filters(self):
        return [
            {
                "id": user_id,
                "command": self.get([user_id])
            } for user_id in self.get_all_active_users()
        ]
