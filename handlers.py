from aiogram.exceptions import TelegramBadRequest

import keyboard

from aiogram import F, Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart

from functions import is_subscribed

dp = Dispatcher()

nl = '\n'
not_subscribed_text = lambda g: f"Вы не подписаны на {nl}{nl.join(g)}"


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    not_subscribed = await is_subscribed(message)
    if not_subscribed:
        await message.answer(not_subscribed_text(not_subscribed), reply_markup=keyboard.check_subscription())
    else:
        await message.answer("Главное меню:", reply_markup=keyboard.main_menu())


@dp.callback_query(keyboard.StartCB.filter(F.check == "check"))
async def check_sub_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from check_subscription button
    """
    not_subscribed = await is_subscribed(query)
    if not_subscribed:
        try:
            await query.message.edit_text(not_subscribed_text(not_subscribed), reply_markup=keyboard.check_subscription())
        except TelegramBadRequest:
            pass
    else:
        await query.message.edit_text("Главное меню:", reply_markup=keyboard.main_menu())

@dp.callback_query(keyboard.MainMenuCB.filter(F.callback == keyboard.MainMenu.catalog))
async def catalog_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from catalog button
    """
    try:
        await query.message.edit_text("Категории товаров", reply_markup=keyboard.main_menu())
    except TelegramBadRequest:
        pass

@dp.callback_query(keyboard.MainMenuCB.filter(F.callback == keyboard.MainMenu.shopping_cart))
async def shopping_cart_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from shopping_cart button
    """
    try:
        await query.message.edit_text("Корзина", reply_markup=keyboard.main_menu())
    except TelegramBadRequest:
        pass


@dp.callback_query(keyboard.MainMenuCB.filter(F.callback == keyboard.MainMenu.faq))
async def faq_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from faq button
    """
    try:
        await query.message.edit_text("FAQ", reply_markup=keyboard.main_menu())
    except TelegramBadRequest:
        pass