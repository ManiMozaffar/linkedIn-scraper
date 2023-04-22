import logging


import requests


from services.tech.factory import KeyWordCrud
from services.tel_users.factory import TelegramCrud
from db import get_app_settings


class AdsManager(TelegramCrud, KeyWordCrud):
    _context = None

    @property
    def context(self):
        if self._context is None:
            self._context = self.get_context
        return self._context

    def forward_message(self, message_id, from_chat_id, ads_keywords):
        logging.info(f"ads_keywords={ads_keywords}")
        token = get_app_settings().telegram_token
        all_related_users = self.union_related_user_tech(ads_keywords)
        for user in all_related_users:
            evaluation = self.eval(
                context=self.context,
                user_expression=self.get_user_expression(user),
                ads_keywords=ads_keywords
            )
            if evaluation.get("evaluation"):
                payload = {
                    "chat_id": user,
                    "from_chat_id": from_chat_id,
                    "message_id": message_id
                }
                url = f"https://api.telegram.org/bot{token}/forwardMessage"
                response = requests.Session().post(url, json=payload)
                if response.status_code != 200 or not response.json(
                ).get("ok"):
                    logging.error(
                        f"Telegram did not forward because: {response.text}"
                    )
                    if "bot was blocked by the user" in response.json().get("description", ""):
                        self.delete_user(user)


async def send_message_to_filtered_users(
        redis_db, message_id, from_chat_id, ads_keywords
):
    AdsManager(redis_db()).forward_message(
        message_id, from_chat_id, ads_keywords
    )
