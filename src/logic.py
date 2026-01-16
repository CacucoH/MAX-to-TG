import aiohttp
import aiofiles
import os
import MaxBridge
import uuid
import logging
import io
from PIL import Image

from shared import BASE_FILES_PATH, USER_AGENT


async def get_status(msg) -> str:
    match msg:
        case "REMOVED":
            return "Удалено"
        case _:
            return ""
    

async def download_attachment(data: dict, api: MaxBridge.max_api.MaxAPI,
                              chat_id: int, msg_id: int) -> str | None:
    fcontent, fname = await get_file_content(data, api, chat_id, msg_id)
    fpath = await save_file_content(fcontent, fname, chat_id)

    return fpath


async def get_file_content(data: dict, api: MaxBridge.max_api.MaxAPI,
                           chat_id: int, msg_id: int) -> tuple[str, bytes] | None:
    match data.get('_type'):
        case "PHOTO":
            url = data.get('baseUrl')
            try:
                async with aiohttp.ClientSession(headers=USER_AGENT) as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            img = Image.open(io.BytesIO(data))
                            fname = str(uuid.uuid4())
                            ext = img.format.lower()

                            if ext == 'webp':
                                img_rgb = img.convert('RGB')
                                new_data: io.BytesIO = io.BytesIO() # Now store converted bytes
                                img_rgb.save(new_data, 'JPEG', quality=95)
                                data = new_data.getvalue()
                                ext = 'jpeg'
                            
                            fname += '.' + ext
                            
                            return (data, fname)
            except Exception as e:
                logging.error(f"При скачивании фотки из {chat_id}: {e}")

        case "FILE":
            file_id = data.get('fileId')
            if not file_id:
                return
            try:
                return api.get_file(id=file_id, chat_id=str(chat_id), msg_id=str(msg_id))
            except Exception as e:
                logging.error(f"При скачивании файла из {chat_id}: {e}")
        case _:
            return
        

async def save_file_content(data: bytes, fname: str, chat_id: str) -> str | None:
    chat_path = os.path.join(BASE_FILES_PATH, chat_id)
    os.makedirs(chat_path, exist_ok=True)

    full_path = os.path.join(chat_path, fname)

    try:
        async with aiofiles.open(full_path, 'wb') as file:
            await file.write(data)
    except Exception as e:
        logging.error(f"Error during file write: {e}")
    
    return full_path


def sanitize_fast(text: str) -> str:
    # Just sanitize spec chars
    return (text
        .replace('\\', '\\\\')
        .replace('_', '\\_')
        .replace('*', '\\*')
        .replace('[', '\\[')
        .replace(']', '\\]')
        .replace('(', '\\(')
        .replace(')', '\\)')
        .replace('~', '\\~')
        .replace('`', '\\`')
        .replace('>', '\\>')
        .replace('#', '\\#')
        .replace('+', '\\+')
        .replace('-', '\\-')
        .replace('=', '\\=')
        .replace('|', '\\|')
        .replace('{', '\\{')
        .replace('}', '\\}')
        .replace('.', '\\.')
        .replace('!', '\\!')
    )