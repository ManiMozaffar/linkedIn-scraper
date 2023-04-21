from pyrogram import filters, enums, types
from pyrogram.types import Message
from . import bot as app
from . import env
from functools import wraps

channel_id = env.channel_id


def is_user_a_member_of_channel(func):
    @wraps(func)
    async def wrapper(bot: app, message: Message) -> bool:
        user = await bot.get_chat_member(channel_id, message.from_user.id)
        if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.OWNER,
        ]:
            return True
        return False

    return wrapper


def is_not_user_a_member_of_channel(func):
    @wraps(func)
    async def wrapper(bot: app, message: Message) -> bool:
        user = await bot.get_chat_member(channel_id, message.from_user.id)
        if user.status in [
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.MEMBER,
            enums.ChatMemberStatus.OWNER,
        ]:
            return False
        return True

    return wrapper
