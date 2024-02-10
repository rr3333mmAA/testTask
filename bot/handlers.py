from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import keyboard

from aiogram import F, Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram.filters import CommandStart

from db import Database
from functions import is_subscribed
from payments import YooKassa
from excel import append_data_to_excel

dp = Dispatcher()

nl = '\n'
not_subscribed_text = lambda g: f"Вы не подписаны на {nl}{nl.join(g)}"



class AddToCart(StatesGroup):
    """
    This class represents states for adding product to the cart
    """
    product = State()
    quantity = State()
    accept = State()

class CartProduct(StatesGroup):
    """
    This class represents states for product in the cart
    """
    product = State()

class Address(StatesGroup):
    """
    This class represents states for address
    """
    address = State()

class Payment(StatesGroup):
    """
    This class represents states for payment
    """
    payment = State()

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    await state.clear()
    Database.add_user(message.from_user.id)
    not_subscribed = await is_subscribed(message)
    if not_subscribed:
        await message.answer(not_subscribed_text(not_subscribed), reply_markup=keyboard.check_subscriptionKB())
    else:
        await message.answer("Главное меню:", reply_markup=keyboard.main_menuKB())


@dp.callback_query(lambda c: c.data.endswith(":Назад"))
async def back_handler(query: CallbackQuery, state: FSMContext) -> None:
    # TODO: Change it
    await state.clear()
    try:
        await query.message.edit_text("Главное меню:", reply_markup=keyboard.main_menuKB())
    except TelegramBadRequest:
        pass


@dp.callback_query(keyboard.StartCB.filter(F.check == "check"))
async def check_sub_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from check_subscription button
    """
    not_subscribed = await is_subscribed(query)
    if not_subscribed:
        try:
            await query.message.edit_text(not_subscribed_text(not_subscribed), reply_markup=keyboard.check_subscriptionKB())
        except TelegramBadRequest:
            pass
    else:
        await query.message.edit_text("Главное меню:", reply_markup=keyboard.main_menuKB())


@dp.callback_query(keyboard.MainMenuCB.filter(F.callback == keyboard.MainMenu.catalog))
async def catalog_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from catalog button
    """
    try:
        await query.message.edit_text("Категории товаров", reply_markup=keyboard.catalogKB())
    except TelegramBadRequest:
        pass


@dp.callback_query(lambda c: c.data.startswith("catalog:"))
async def category_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from category buttons
    """
    category = query.data.split(":")[1]
    try:
        await query.message.edit_text(f"Товары в категории {category}", reply_markup=keyboard.categoryKB(category))
    except TelegramBadRequest:
        pass


@dp.callback_query(lambda c: c.data.startswith("subcategory:"))
async def subcategory_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from subcategory buttons
    """
    subcategory = query.data.split(":")[1]
    try:
        await query.message.edit_text(f"Товары в подкатегории {subcategory}", reply_markup=keyboard.subcategoryKB(subcategory))
    except TelegramBadRequest:
        pass


@dp.callback_query(lambda c: c.data.startswith("product:"))
async def product_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from product buttons
    """
    await state.set_state(AddToCart.product)
    product = query.data.split(":")[1]
    product_details = Database.get_product(product)
    await state.update_data(product=product)
    try:
        await query.message.edit_text(f"Количество - {product_details[1]}\nОписание {product}:\n{product_details[2]}\n\nЦена: {product_details[4]}", reply_markup=keyboard.add_to_cartKB())     # TODO: Add image
    except TelegramBadRequest:
        pass


@dp.callback_query(keyboard.AddToCartCB.filter(F.callback == keyboard.AddToCart.buy), AddToCart.product)
async def add_to_cart_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from add_to_cart button
    """
    await state.set_state(AddToCart.quantity)
    data = await state.get_data()
    product_details = Database.get_product(data["product"])
    await query.message.edit_text(f"Количество - {product_details[1]}\nВведите количество товара")


@dp.message(AddToCart.quantity)
async def quantity_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with quantity of product
    """
    await state.update_data(quantity=message.text)
    data = await state.get_data()
    product = data["product"]
    product_details = Database.get_product(product)
    quantity = data["quantity"]
    if not quantity.isdigit() or int(quantity) < 0 or not Database.check_quantity(product, int(quantity)):
        await message.answer("Товара в таком количестве нет на складе")
        await message.answer(f"Количество - {product_details[1]}\nОписание {product}:\n{product_details[2]}\n\nЦена: {product_details[4]}", reply_markup=keyboard.cartKB())
        await state.set_state(AddToCart.product)
    elif int(quantity) == 0:
        await message.answer("Количество товара не может быть равно 0. Попробуйте еще раз")
    else:
        await state.set_state(AddToCart.accept)
        await message.answer(f"Добавить {product} в корзину в количестве {quantity}?", reply_markup=keyboard.acceptKB())


@dp.callback_query(keyboard.AcceptCB.filter(F.accept == "accept"), AddToCart.accept)
async def accept_product_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from accept button
    """
    data = await state.get_data()
    product_details = Database.get_product(data["product"])
    Database.add_to_cart(query.from_user.id, data["product"], int(data["quantity"]), product_details[4])
    await state.clear()
    await shopping_cart_handler(query)


@dp.callback_query(keyboard.CartProductCB.filter(F.callback == keyboard.CartProduct.remove), CartProduct.product)
async def remove_product_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from delete_product buttons
    """
    data = await state.get_data()
    product = data["product"]
    Database.delete_product(query.from_user.id, product)
    await state.clear()
    await shopping_cart_handler(query)


@dp.callback_query(keyboard.MainMenuCB.filter(F.callback == keyboard.MainMenu.shopping_cart))
async def shopping_cart_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from shopping_cart button
    """
    cart_products = Database.get_cart_products(query.from_user.id)
    products = [f"{product[0]}: {product[1]}" for product in cart_products]
    total = Database.get_user_amount(query.from_user.id)
    try:
        await query.message.edit_text(f"Корзина:{nl}{nl.join(products)}\n\nИтого - {total if total is not None else 0}", reply_markup=keyboard.cartKB(query.from_user.id))
    except TelegramBadRequest:
        pass

@dp.callback_query(lambda c: c.data.startswith("cart_product:"))
async def cart_product_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from cart_product buttons
    """
    await state.set_state(CartProduct.product)
    product = query.data.split(":")[1]
    product_details = Database.get_product(product)
    await state.update_data(product=product)
    try:
        await query.message.edit_text(f"Описание {product_details[0]}:\n{product_details[2]}\n\nЦена: {product_details[4]}", reply_markup=keyboard.cart_productKB())
    except TelegramBadRequest:
        pass

@dp.callback_query(keyboard.AddressCB.filter(F.address == "address"))
async def address_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from address button
    """
    try:
        await query.message.edit_text("Введите адрес доставки")
        await state.set_state(Address.address)
    except TelegramBadRequest:
        pass

@dp.message(Address.address)
async def address_message_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with address
    """
    await state.update_data(address=message.text)
    await message.answer(f"Адрес доставки {message.text}", reply_markup=keyboard.acceptKB())


@dp.callback_query(keyboard.AcceptCB.filter(F.accept == "accept"), Address.address)
async def accept_address_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from accept button
    """
    data = await state.get_data()
    Database.change_address(query.from_user.id, data["address"])
    await state.clear()

    products = Database.get_cart_products(query.from_user.id)
    description = nl.join(f'{product} x {quantity}' for product, quantity in products)
    payment = YooKassa(Database.get_user_amount(query.from_user.id), description)
    payment_url = await payment.get_payment_url()
    await state.set_state(Payment.payment)
    await state.update_data(payment=payment)

    await query.message.edit_text("Оплата заказа", reply_markup=keyboard.paymentKB(payment_url))


@dp.callback_query(lambda c: c.data == "check_payment", Payment.payment)
async def check_payment_handler(query: CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives callback queries from check_payment button
    """
    data = await state.get_data()
    payment_status = await data['payment'].get_payment_status()
    if payment_status == "succeeded":
        await query.answer("Оплата прошла успешно")
        await state.clear()
        await query.message.edit_text("Главное меню:", reply_markup=keyboard.main_menuKB())
        products = Database.get_cart_products(query.from_user.id)
        append_data_to_excel([
            query.from_user.username,
            Database.get_user_address(query.from_user.id),
            ', '.join(f'{product}({quantity})' for product, quantity in products),
            str(Database.get_user_amount(query.from_user.id))+ " руб."
        ])
        Database.update_quantity(query.from_user.id)
        Database.clear_cart(query.from_user.id)
    elif payment_status == "canceled":
        await query.answer("Оплата отменена")
        await state.clear()
        await shopping_cart_handler(query)
    else:
        await query.answer("Оплата не прошла")



@dp.callback_query(keyboard.MainMenuCB.filter(F.callback == keyboard.MainMenu.faq))
async def faq_handler(query: CallbackQuery) -> None:
    """
    This handler receives callback queries from faq button
    """
    try:
        await query.message.edit_text("FAQ", reply_markup=keyboard.main_menuKB())
    except TelegramBadRequest:
        pass
