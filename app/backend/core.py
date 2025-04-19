import asyncio

from db import Database

db = Database()


async def push_record(chat_id: int, chat_history):
    request_id = db.add_new_request(chat_id)
    asyncio.create_task(process_request(chat_id, request_id, chat_history))
    return request_id


async def process_request(chat_id: int, request_id: int, chat_history):
    db.update_request_status(request_id, "intent", "in work")
    await asyncio.sleep(1)
    intent = "test"
    db.update_request_status(request_id, "intent", "done")
    db.update_chat_summary_intent(chat_id, intent)
    db.update_request_status(request_id, "emotion", "in work")
    await asyncio.sleep(1)
    emotion = "happy"
    db.update_request_status(request_id, "emotion", "done")
    db.update_request_emotion(request_id, emotion)
