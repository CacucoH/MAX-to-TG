"""
    Useful decorators
"""
import functools
import os


def is_owner(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        events = args[0] if args else None
        if not events:
            return
        
        admin_chat_id = os.getenv('tg_userid_chat')
        sender = events.sender_id

        if str(sender) != admin_chat_id:
            GOODBYE_MSG = os.getenv("REPLY_UNKNOWN_USER", "Not authorized")
            print(f"ATTENTION! User {sender} tried to access the bot. Aborted.")
            # await events.client.send_message(sender, GOODBYE_MSG)
            return

        return await func(*args, **kwargs)
    return wrapper