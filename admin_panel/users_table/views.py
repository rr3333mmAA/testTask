import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from .models import Users, Catalog, Category, Cart


async def send_message_to_users(selected_users, message):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    for user_id in selected_users:
        try:
            await bot.send_message(chat_id=int(user_id), text=message)
        except Exception as e:
            print(e)


def send_message(request):
    selected_users = request.POST.getlist('selected_users')
    message = request.POST.get('message')

    # Run send_message_to_users
    asyncio.run(send_message_to_users(selected_users, message))

    return JsonResponse({'success': True})


def user_list(request):
    users = Users.objects.all()
    catalog = Catalog.objects.all()
    categories = Category.objects.all()
    cart = Cart.objects.all()
    return render(request, 'index.html', {'users': users, 'catalog': catalog, 'categories': categories, 'cart': cart})
