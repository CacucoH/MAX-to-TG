import asyncio
import logging
import os

from aiogram import Dispatcher
from dotenv import load_dotenv
from MaxBridge import MaxAPI

from event_handlers import queue_checker, server_events_handler
from shared import BASE_FILES_PATH, BOT, PRIVATE_ROUTER

load_dotenv(r"./data/config/.env")


dp = Dispatcher()
MAX_AUTH_TOKEN = os.getenv("max_token")
os.makedirs(BASE_FILES_PATH, exist_ok=True)


async def main():
    # Инициализация API с пользовательским обработчиком событий
    api = MaxAPI(auth_token=MAX_AUTH_TOKEN, on_event=server_events_handler)
    try:
        polling = asyncio.create_task(queue_checker(api))
        dp.include_router(PRIVATE_ROUTER)
        await dp.start_polling(BOT)
    finally:
        logging.info("Terminating...")
        polling.cancel()


if __name__ == "__main__":
    asyncio.run(main())
