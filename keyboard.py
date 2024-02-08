# TODO: callback_data has limitations

import json
from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

catalog_json = json.load(open("catalog.json"))

class StartCB(CallbackData, prefix="start"):
    check: str


class MainMenu(str, Enum):
    catalog = "Каталог"
    shopping_cart = "Корзина"
    faq = "FAQ"
    back = "Назад"


class MainMenuCB(CallbackData, prefix="main_menu"):
    callback: MainMenu

class Product(str, Enum):
    buy = "Купить"
    back = "Назад"

class ProductCB(CallbackData, prefix="product"):
    callback: Product


def check_subscriptionKB():
    """
    This function returns InlineKeyboardMarkup with buttons to check subscription
    """
    check_button = InlineKeyboardButton(text="Проверить подписку", callback_data=StartCB(check="check").pack())
    return InlineKeyboardMarkup(inline_keyboard=[[check_button]])


def main_menuKB():
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


def catalogKB():
    """
    This function returns InlineKeyboardMarkup with catalog buttons
    """
    builder = InlineKeyboardBuilder()
    for category in catalog_json:
        builder.button(
            text=category,
            callback_data=f"catalog:{category}",
        )
    return builder.as_markup()


def categoryKB(category: str):
    """
    This function returns InlineKeyboardMarkup with category buttons
    """
    builder = InlineKeyboardBuilder()
    for subcategory in catalog_json[category]:
        builder.button(
            text=subcategory,
            callback_data=f"subcategory:{category}:{subcategory}",
        )
    return builder.as_markup()


def subcategoryKB(category: str, subcategory: str):
    """
    This function returns InlineKeyboardMarkup with subcategory buttons
    """
    builder = InlineKeyboardBuilder()
    for product in catalog_json[category][subcategory]:
        builder.button(
            text=product,
            callback_data=f"product:{product}",
        )
    return builder.as_markup()

def productKB():
    """
    This function returns InlineKeyboardMarkup with product buttons
    """
    builder = InlineKeyboardBuilder()
    for attr in Product:
        builder.button(
            text=attr.value,
            callback_data=ProductCB(callback=attr),
        )
    return builder.as_markup()





