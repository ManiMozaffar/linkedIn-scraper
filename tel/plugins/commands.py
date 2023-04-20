from . import bot as app
from pyrogram import filters, enums, types
import requests
import loguru
import os
from . import env
from .filters import is_user_a_member_of_channel, is_not_user_a_member_of_channel
from . import texts


# Commands Section
@app.on_message(filters.command("show") & filters.private)
async def show_keywords(_, message: types.Message):
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
@is_user_a_member_of_channel
async def get_info(_, message: types.Message):
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
    text = texts.START_MESSAGE
    await message.reply_text(
        text,
        parse_mode=enums.ParseMode.MARKDOWN,
    )


@app.on_message(filters.private & ~filters.me)
@is_user_a_member_of_channel
async def update_expression(_, message: types.Message):
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


@is_not_user_a_member_of_channel
async def not_member(_, message: types.Message):
    await message.reply_text(
        "Please Join The Channel \n https://t.me/linkedin_python",
        reply_to_message_id=message.reply_to_message_id
    )
