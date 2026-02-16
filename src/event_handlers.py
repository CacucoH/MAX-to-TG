import asyncio
import json
import logging

import MaxBridge
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile

from logic import download_attachment, get_status, sanitize_fast
from shared import BOT, PHOTO_EXT, QUEUE, TG_CHAT_ID


def server_events_handler(event_data):
    """
    Пользовательская функция для обработки входящих событий от сервера.
    """
    opcode = event_data.get("opcode")

    match opcode:
        # New msg
        case 128:
            QUEUE.put({"MESSAGE": event_data})
        # Reaction added
        case 156:
            pass
        case 136:
            QUEUE.put({"FILE": event_data})
        case _:
            logging.debug(f"Событие от сервера (Opcode {opcode}): {
                    json.dumps(event_data, indent=2, ensure_ascii=False)
                }")


async def send_message(event_data, api: MaxBridge.MaxAPI):
    logging.info(f"Получено новое сообщение: {
            json.dumps(event_data, indent=2, ensure_ascii=False)
        }")
    downloaded_media = []
    payload: dict = event_data.get("payload")
    if not payload:
        return

    message: dict = payload.get("message")
    message_id = message.get("id")
    chat_id = payload.get("chatId")

    status = message.get("status")
    prnt_msg_status = await get_status(status)

    check_forwarded = message.get("link")
    if check_forwarded and check_forwarded.get("type") == "FORWARD":
        # Message was forwarded
        message = check_forwarded.get("message")

        fwd_sender_id = str(message.get("sender"))
        fwd_sender_instance = api.get_contact_details([fwd_sender_id])
        fwd_sender_name = await get_sender_name(fwd_sender_instance)

        # Send either username or id if username not present
        prnt_msg_status += f"\(Переслано от {
            fwd_sender_name if fwd_sender_instance else fwd_sender_id
        }\)"

    attachments = message.get("attaches")

    # Download any attachment
    tasks = [
        download_attachment(attch, api, chat_id=str(chat_id), msg_id=str(message_id))
        for attch in attachments
    ]

    # All parallel donwloaded files
    downloaded_media = await asyncio.gather(*tasks)

    sender_id = str(message.get("sender"))
    sender_instance = api.get_contact_details([sender_id])
    sender_name = await get_sender_name(sender_instance)

    msg_to_send: str = "{msgstatus} сообщение от *{user}* в *{chat}*: {text}"
    msg_text = sanitize_fast(message.get("text"))

    chat_name = "Unknown"
    chat_instance_full = api.get_chat_by_id(str(chat_id))
    chat_type = chat_instance_full.get("type")

    if chat_instance_full:
        if chat_type == "DIALOG":
            chat_name = "личке"

        elif chat_type == "CHAT":
            chat_name = chat_instance_full.get("title")

    msg_to_send = (
        msg_to_send.replace("{msgstatus}", prnt_msg_status)
        .replace("{text}", msg_text)
        .replace("{user}", sender_name)
        .replace("{chat}", chat_name)
    )

    await BOT.send_message(
        chat_id=TG_CHAT_ID, text=msg_to_send, parse_mode=ParseMode.MARKDOWN_V2
    )
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
    ext = fpath.split(".")[-1]
    if ext in PHOTO_EXT:
        await BOT.send_photo(chat_id=chat_id, photo=FSInputFile(fpath))
        return
    await BOT.send_document(chat_id=TG_CHAT_ID, document=FSInputFile(fpath))


async def get_sender_name(sender_instance) -> str:
    sender_instance_dict = (
        sender_instance.get("payload").get("contacts")[0].get("names")[0]
    )
    sender_name = sender_instance_dict.get("firstName") + sender_instance_dict.get(
        "lastName"
    )
    return sender_name


FUNC_MAP = {
    "MESSAGE": send_message,
    # "FILE": file_download,
}


# @wrappers.is_owner
# @PRIVATE_ROUTER.message()
# async def echo_reply(msg: Message):
#     msg.answer("здарова я живой")
