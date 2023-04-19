import requests
from db import get_app_settings
from typing import Union
import logging


def send_message_to_telegram(
        chat_id, message_text, button_text, button_url, 
) -> Union[list, None]:
    payload = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'Markdown',
        'reply_markup': {
            'inline_keyboard': [[{
                'text': button_text,
                'url': button_url
            }]]
        }
    }
    token = get_app_settings().telegram_token
    resp = requests.post(
        f'https://api.telegram.org/bot{token}/sendMessage',
        json=payload
    )
    if resp.status_code != 200 or not resp.json()["ok"]:
        logging.error(
            f"Telegram Message Ddin't sent\nresp={resp.text}\ntext={message_text}"
        )
        return None
    else:
        return resp.json()["result"]
