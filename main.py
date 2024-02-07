import logging
import sys
import asyncio
from os import getenv

from aiogram import Bot
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from handlers import dp

# Loading .env file and initialize bot token as TOKEN
load_dotenv()
TOKEN = getenv("BOT_TOKEN")

async def main() -> None:
    # Initialize Bot instance
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())








