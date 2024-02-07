from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class StartCB(CallbackData, prefix="start"):
    check: str


class MainMenu(str, Enum):
    catalog = "Каталог"
    shopping_cart = "Корзина"
    faq = "FAQ"


class MainMenuCB(CallbackData, prefix="main_menu"):
    callback: MainMenu


def check_subscription():
    """
    This function returns InlineKeyboardMarkup with buttons to check subscription
    """
    check_button = InlineKeyboardButton(text="Проверить подписку", callback_data=StartCB(check="check").pack())
    return InlineKeyboardMarkup(inline_keyboard=[[check_button]])


def main_menu():
    """
    This function returns InlineKeyboardMarkup with main menu buttons
    """
    builder = InlineKeyboardBuilder()
    for attr in MainMenu:
        builder.button(
            text=attr.value,
            callback_data=MainMenuCB(callback=attr),
        )
    return builder.as_markup()


def catalog():
    """
    This function returns InlineKeyboardMarkup with catalog buttons
    """
    builder = InlineKeyboardBuilder()




