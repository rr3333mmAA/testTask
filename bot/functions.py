from os import getenv

from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, CallbackQuery


async def is_subscribed(mesquery: Message | CallbackQuery) -> list:
    """
    This function checks if user is subscribed to all channels and groups
    """
    not_subscribed = []
    channels2sub = getenv("CHANNELS_TO_SUBSCRIBE").split(", ")

    # Check if user is subscribed to all channels and groups
    for channel in channels2sub:
        result = await mesquery.bot.get_chat_member(channel, mesquery.from_user.id)
        if result.status == ChatMemberStatus.LEFT:
            not_subscribed.append(channel)

    return not_subscribed
