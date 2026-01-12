import queue
import os

from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot


TG_BOT_TOKEN = os.getenv('tg_token')
TG_SESSION_NAME = os.getenv('tg_session_name')
TG_CHAT_ID = os.getenv('tg_userid_chat')
BOT = Bot(
        token=TG_BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.MARKDOWN_V2
            )
        )
QUEUE = queue.Queue()