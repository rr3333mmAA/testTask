from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, CallbackQuery

from config import channels2subscribe


async def is_subscribed(mesquery: Message | CallbackQuery) -> list:
    """
    This function checks if user is subscribed to all channels and groups
    """
    not_subscribed = []

    # Check if user is subscribed to all channels and groups
    for channel in channels2subscribe:
        result = await mesquery.bot.get_chat_member(channel, mesquery.from_user.id)
        if result.status == ChatMemberStatus.LEFT:
            not_subscribed.append(channel)

    return not_subscribed