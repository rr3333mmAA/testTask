import logging
import sys
import asyncio
from os import getenv

from aiogram import Bot
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from handlers import dp
from db import init_db, Database

# Load environment variables from .env file
load_dotenv()
TOKEN = getenv("BOT_TOKEN")


async def main() -> None:
    # Initialize Bot instance
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # Initialize database and create tables
    init_db("testtask")
    Database.create_tables()
    # Database.load_starter_catalog()  # Load starter catalog from starter_catalog.json (TODO: already loaded)

    # Run events dispatching
    await dp.start_polling(bot)

    # Close database connection
    Database.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
