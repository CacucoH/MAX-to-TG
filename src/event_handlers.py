import json
import asyncio
import MaxBridge
import logging

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

import wrappers
from shared import BOT, TG_CHAT_ID, QUEUE, PRIVATE_ROUTER


def server_events_handler(event_data):
    """
    Пользовательская функция для обработки входящих событий от сервера.
    """
    opcode = event_data.get("opcode")


    # New msg
    if opcode == 128:
        QUEUE.put(event_data)
    else:
        logging.debug(f"Событие от сервера (Opcode {opcode}): {json.dumps(event_data, indent=2, ensure_ascii=False)}")


async def send_message(event_data, api: MaxBridge.MaxAPI):
    logging.info(f"Получено новое сообщение: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
    payload: dict = event_data.get('payload')
    if not payload:
        return
    
    chat_id = payload.get('chatId')
    message = payload.get('message')
    
    sender_id = message.get('sender')
    msg_to_send: str = "Сообщение от *{user}* в *{chat}*: {text}"
    # if message.get('type') == 'USER':
    #     msg_to_send += 'пользователя '
    # else:
    #     msg_to_send += 'хз кого '
    
    sender_instance_full = api.get_contact_details([sender_id])
    sender_instance_dict = sender_instance_full.get("payload").get("contacts")[0].get("names")[0]
    sender_name = sender_instance_dict.get("firstName") + sender_instance_dict.get("lastName")

    chat_name = "Unknown"
    chat_instance_full = api.get_chat_by_id(str(chat_id))
    chat_type = chat_instance_full.get("type")

    if chat_instance_full:
        if chat_type == 'DIALOG':
            chat_name = 'личке'

        elif chat_type == 'CHAT':
            chat_name = chat_instance_full.get("title")

    msg_to_send = msg_to_send.replace('{text}', message.get('text')) \
                             .replace('{user}', sender_name) \
                             .replace('{chat}', chat_name)

    await BOT.send_message(chat_id=TG_CHAT_ID, text=msg_to_send, parse_mode=ParseMode.MARKDOWN_V2)
    logging.info("Retransmitted msg to user")


async def queue_checker(api: MaxBridge.MaxAPI):
    while True:
        item = QUEUE.get()
        if item:
            await send_message(item, api)
            continue
        
        asyncio.sleep(1)
    

@wrappers.is_owner
@PRIVATE_ROUTER.message()
async def echo_reply(msg: Message):
    msg.answer("здарова я живой")