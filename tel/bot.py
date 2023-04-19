import os

from dotenv import load_dotenv
from pyrogram import Client, filters, enums, types
import requests
import loguru


load_dotenv()

api_id = os.getenv("APP_ID")
api_hash = os.getenv("HASH_ID")
bot_token = os.getenv("TELEGRAM_TOKEN")
channel_id = os.getenv("TELEGRAM_CHAT_ID")


app = Client(
    "my_bot", bot_token=bot_token, workers=1, api_id=api_id, api_hash=api_hash
)


async def is_user_a_member(message: types.Message, channel_id=channel_id):
    user = await app.get_chat_member(channel_id, message.from_user.id)
    if user.status in [
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.MEMBER,
        enums.ChatMemberStatus.OWNER,
    ]:
        return True
    else:
        await message.reply_text(
            "Please Join The Channel \n https://t.me/linkedin_python",
            reply_to_message_id=message.reply_to_message_id
        )


@app.on_message(filters.command("show") & filters.private)
async def show_keywords(_, message: types.Message):
    if await is_user_a_member(message):
        text = requests.get(
            "http://main_app:8000/api/tech/keywords"
        ).json().get("result")
        text = ' \n'.join(text) + (
            "\n\n\nFor reference please check this url:"
        ) + (
            "\nhttps://github.com/ManiMozaffar/linkedIn-scraper/blob/main/src/services/tech/loaddata.py"
        )
        await message.reply_text(
            text,
            reply_to_message_id=message.reply_to_message_id
        )


@app.on_message(filters.command("info") & filters.private)
async def get_info(_, message: types.Message):
    if await is_user_a_member(message):
        loguru.logger.info(
            f"Recieved message {message.from_user.id}: {message.text}"
        )
        text = requests.get(
            f"http://main_app:8000/api/telegram/user/{int(message.from_user.id)}"
        ).json().get("result", [])
        text = text[0] if len(text) == 1 else "No Query Found"
        loguru.logger.info(f"Sent message {message.from_user.id}: {text}")
        await message.reply_text(
            text,
            reply_to_message_id=message.reply_to_message_id
        )


@app.on_message(filters.command("start") & filters.private)
async def welcome(_, message: types.Message):
    text = """
Hey!
Welcome to linkedin scrapper, are you annoyed by linkedin terrible filters? don't worry, I've got your back!
I have a very cool feature in this bot, I have called it Nested Logical Expression Filter Query.
In a very simple language, you can write your filters and query in pure PYTHON expression!
\n\nFor example, I want to get hird in netherlands where to work as backend engineer with django or fastapi, if there's a vuejs i can work as frontend too, or even full stack, also I want to only work in germany, so how do I write such hard query?
Too easy! ```(django or fastapi) and (backend or (fullstack and vuejs) or (frontend and vuejs)) and germany```
You only need 1 day of python knowledge to write your own logical expression :)
Please use /show command to see all the possible namespaces and keywords you can filter.
You may use /info to check your current query

If you want to setup your filter, simply write it to me here.

Remember, You must be a member of main channel to be able to use this bot:)
@linkedin_python

Also, don't forget to star my project in github or contribute if you found it cool/useful :)
\n https://github.com/ManiMozaffar/linkedIn-scraper
"""
    await message.reply_text(
        text,
        parse_mode=enums.ParseMode.MARKDOWN,
    )


@app.on_message(filters.private & ~filters.me)
async def update_expression(_, message: types.Message):
    if await is_user_a_member(message):
        loguru.logger.info(
            f"Recieved message {message.from_user.id}: {message.text}"
        )
        payload = {"expression": str(message.text)}
        resp: dict = requests.put(
            f"http://main_app:8000/api/telegram/user/{int(message.from_user.id)}",
            json=payload
        ).json()
        if resp.get("success"):
            text = "Thanks, your query was saved successfully"
        else:
            error = resp.get('error')
            text = f"Your query is not done correctly, because: {error}"
            text += "\n\nPlease write /show to see all available namspaces"
            text += "\n or /start to see the how-to-use guide!"

        loguru.logger.info(f"Sent message {message.from_user.id}: {text}")
        await message.reply_text(
            text,
            reply_to_message_id=message.reply_to_message_id
        )

if __name__ == "__main__":
    app.run()
