from dotenv import load_dotenv
import os


class EnvReader:
    def __init__(self):
        if not (os.path.exists(".env")):
            raise IOError(".env file Not Exist")

        load_dotenv()
        self.api_id = os.getenv("APP_ID")
        self.api_hash = os.getenv("HASH_ID")
        self.bot_token = os.getenv("TELEGRAM_TOKEN")
        self.channel_id = os.getenv("TELEGRAM_CHAT_ID")
