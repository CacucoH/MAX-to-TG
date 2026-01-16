import queue
import logging
import datetime
import os

from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Router

import my_filters

logging.basicConfig(
        level=logging.INFO, 
        format="[%(levelname)s] - %(asctime)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        # filename=f"./src/logs/log_{TODAY}.log",
        filemode="a"
    )

### config
DEV = False
TG_BOT_TOKEN = os.getenv('tg_token')
TG_SESSION_NAME = os.getenv('tg_session_name')
TG_CHAT_ID = os.getenv('tg_userid_chat')
BOT = Bot(
        token=TG_BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.MARKDOWN_V2
            )
        )
### tech
QUEUE = queue.Queue()
PRIVATE_ROUTER = Router()
PRIVATE_ROUTER.message.filter(
    my_filters.ChatTypeFilter("private")
)

### misc
TODAY = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
BASE_FILES_PATH = r'./data/files' if DEV else r'/app/data/files/'
USER_AGENT = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0"}
PHOTO_EXT = {'jpg', 'jpeg', 'png', 'gif'}
