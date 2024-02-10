from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import Database


class StartCB(CallbackData, prefix="start"):
    check: str

class AcceptCB(CallbackData, prefix="accept"):
    accept: str

class AddressCB(CallbackData, prefix="address"):
    address: str

class MainMenu(str, Enum):
    catalog = "Каталог"
    shopping_cart = "Корзина"
    faq = "FAQ"


class MainMenuCB(CallbackData, prefix="main_menu"):
    callback: MainMenu

class AddToCart(str, Enum):
    buy = "Добавить в корзину"
    # back = "Назад"        # TODO: add back button

class AddToCartCB(CallbackData, prefix="add_to_cart"):
    callback: AddToCart

class CartProduct(str, Enum):
    remove = "Удалить"
    back = "Назад"

class CartProductCB(CallbackData, prefix="cart_product"):
    callback: CartProduct


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
    categories = Database.get_categories()
    for category in categories:
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
    subcategories = Database.get_subcategories(category)
    for subcategory in subcategories:
        builder.button(
            text=subcategory,
            callback_data=f"subcategory:{subcategory}",
        )
    return builder.as_markup()


def subcategoryKB(subcategory: str):
    """
    This function returns InlineKeyboardMarkup with subcategory buttons
    """
    builder = InlineKeyboardBuilder()
    products = Database.get_products(subcategory)
    for product in products:
        builder.button(
            text=product[0],
            callback_data=f"product:{product[0]}",
        )
    return builder.as_markup()

def add_to_cartKB():
    """
    This function returns InlineKeyboardMarkup with product buttons
    """
    builder = InlineKeyboardBuilder()
    for attr in AddToCart:
        builder.button(
            text=attr.value,
            callback_data=AddToCartCB(callback=attr),
        )
    return builder.as_markup()

def cartKB(user_tgid: int):
    """
    This function returns InlineKeyboardMarkup with cart buttons
    """
    builder = InlineKeyboardBuilder()
    products = Database.get_cart_products(user_tgid)
    for product in products:
        builder.button(
            text=product[0],
            callback_data=f"cart_product:{product[0]}",
        )
    address_button = InlineKeyboardButton(text="Адрес доставки", callback_data=AddressCB(address="address").pack())
    builder.add(address_button)
    return builder.as_markup()


def cart_productKB():
    """
    This function returns InlineKeyboardMarkup with cart product buttons
    """
    builder = InlineKeyboardBuilder()
    for attr in CartProduct:
        builder.button(
            text=attr.value,
            callback_data=CartProductCB(callback=attr),
        )
    return builder.as_markup()


def acceptKB():
    """
    This function returns InlineKeyboardMarkup with accept button
    """
    accept_button = InlineKeyboardButton(text="Подтвердить", callback_data=AcceptCB(accept="accept").pack())
    return InlineKeyboardMarkup(inline_keyboard=[[accept_button]])


def paymentKB(url: str):
    """
    This function returns InlineKeyboardMarkup with payment buttons
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="ЮKassa",
        url=url,
    )
    builder.button(
        text="Проверить оплату",
        callback_data="check_payment",
    )
    return builder.as_markup()




