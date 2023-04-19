import logging

import requests

from db import get_app_settings
from .factory import TelegramRetriever


class TelegrmNotifier(TelegramRetriever):
    def forward_message(self, message_id, from_chat_id, all_related_users):
        token = get_app_settings().telegram_token
        for user in all_related_users:
            payload = {
                "chat_id": user,
                "from_chat_id": from_chat_id,
                "message_id": message_id
            }
            url = f"https://api.telegram.org/bot{token}/forwardMessage"
            response = requests.Session().post(url, json=payload)
            if response.status_code != 200 or not response.json(
            ).get("ok"):
                logging.error(response.text)
