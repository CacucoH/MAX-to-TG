import json
import asyncio
import MaxBridge
import logging

from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

import wrappers
from shared import (BOT, TG_CHAT_ID, QUEUE, PHOTO_EXT)
from logic import get_status, download_attachment, sanitize_fast


def server_events_handler(event_data):
    """
    Пользовательская функция для обработки входящих событий от сервера.
    """
    opcode = event_data.get("opcode")


    match opcode:
        # New msg
        case 128:
            QUEUE.put({"MESSAGE":event_data})
        # Reaction added
        case 156:
            pass
        case 136:
            QUEUE.put({"FILE":event_data})
        case _:
            logging.debug(f"Событие от сервера (Opcode {opcode}): {json.dumps(event_data, indent=2, ensure_ascii=False)}")


async def send_message(event_data, api: MaxBridge.MaxAPI):
    logging.info(f"Получено новое сообщение: {json.dumps(event_data, indent=2, ensure_ascii=False)}")
    downloaded_media = []
    payload: dict = event_data.get('payload')
    if not payload:
        return
    
    message : dict = payload.get('message')
    message_id = message.get('id')

    chat_id = payload.get('chatId')
    status = message.get('status')
    attachments = message.get('attaches')

    # Download any attachment
    tasks = [
        download_attachment(attch, api, chat_id=str(chat_id), msg_id=str(message_id))
        for attch in attachments
    ]

    downloaded_media = await asyncio.gather(*tasks) # All parallel donwloaded files
    
    sender_id = message.get('sender')
    msg_to_send: str = "{msgstatus} сообщение от *{user}* в *{chat}*: {text}"
    msg_text = sanitize_fast(message.get('text'))
    sender_instance_full = api.get_contact_details([sender_id])
    sender_instance_dict = sender_instance_full.get("payload").get("contacts")[0].get("names")[0]
    sender_name = sender_instance_dict.get("firstName") + sender_instance_dict.get("lastName")

    chat_name = "Unknown"
    chat_instance_full = api.get_chat_by_id(str(chat_id))
    chat_type = chat_instance_full.get("type")

    prnt_msg_status = await get_status(status)
    if chat_instance_full:
        if chat_type == 'DIALOG':
            chat_name = 'личке'

        elif chat_type == 'CHAT':
            chat_name = chat_instance_full.get("title")

    msg_to_send = msg_to_send.replace('{msgstatus}', prnt_msg_status) \
                             .replace('{text}', msg_text) \
                             .replace('{user}', sender_name) \
                             .replace('{chat}', chat_name)

    await BOT.send_message(chat_id=TG_CHAT_ID, text=msg_to_send, parse_mode=ParseMode.MARKDOWN_V2)
    for attach_path in downloaded_media:
        await send_file_universal(chat_id=TG_CHAT_ID, fpath=attach_path)

    logging.info("Retransmitted msg to user")


async def queue_checker(api: MaxBridge.MaxAPI):
    while True:
        item: dict = QUEUE.get()
        if item:
            command_name, data = next(iter(item.items()))
            callback = FUNC_MAP.get(command_name)
            if not callback:
                continue

            await callback(data, api)
            continue
        
        asyncio.sleep(1)


async def send_file_universal(chat_id: int, fpath: str):
    ext = fpath.split('.')[-1]
    if ext in PHOTO_EXT:
        await BOT.send_photo(chat_id=chat_id, photo=FSInputFile(fpath))
        return
    await BOT.send_document(chat_id=TG_CHAT_ID, document=FSInputFile(fpath))



FUNC_MAP = {
    "MESSAGE": send_message,
    # "FILE": file_download,
}


# @wrappers.is_owner
# @PRIVATE_ROUTER.message()
# async def echo_reply(msg: Message):
#     msg.answer("здарова я живой")