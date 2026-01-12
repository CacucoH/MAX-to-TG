import asyncio
import os
import logging

from dotenv import load_dotenv
load_dotenv(r'./data/config/.env')

from aiogram import Dispatcher
from MaxBridge import MaxAPI

from wrappers import is_owner
from event_handlers import server_events_handler, queue_checker
from shared import BOT, PRIVATE_ROUTER


dp = Dispatcher()
MAX_AUTH_TOKEN = os.getenv('max_token')


async def main():
    # Инициализация API с пользовательским обработчиком событий    
    api = MaxAPI(auth_token=MAX_AUTH_TOKEN, on_event=server_events_handler)

    a = api.get_all_chats()

    try:
        polling = asyncio.create_task(queue_checker(api))
        dp.include_router(PRIVATE_ROUTER)
        await dp.start_polling(BOT)
    finally:
        logging.info("Terminating...")
        polling.cancel()
        
    # print(api.get_all_chats())

asyncio.run(main())