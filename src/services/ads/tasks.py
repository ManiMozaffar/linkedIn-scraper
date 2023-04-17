from services.tech.repositories import KeyWordCrud
from services.tel_users.repositories import TelegramCrud
from db import get_app_settings
import requests

class AdsManager(TelegramCrud, KeyWordCrud):
    _context = None

    @property
    def context(self):
        if self._context is None:
            self._context = self.get_context
        return self._context

    def forward_message(self, message_id, from_chat_id, ads_keywords):
        print(ads_keywords)
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
                print(user)
                print(payload)
                url = f"https://api.telegram.org/bot{token}/forwardMessage"
                response = requests.post(url, json=payload)
                print(response.text)



async def send_message_to_filtered_users(
        redis_db, message_id, from_chat_id, ads_keywords
):
    AdsManager(redis_db()).forward_message(
        message_id, from_chat_id, ads_keywords
    )
