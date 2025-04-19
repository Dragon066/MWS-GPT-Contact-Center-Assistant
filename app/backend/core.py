import asyncio

from db import Database

db = Database()


async def push_record(chat_id: int, chat_history):
    request_id, is_new = db.add_new_request(chat_id, len(chat_history))
    if is_new:
        asyncio.create_task(process_request(chat_id, request_id, chat_history))
    return request_id


async def process_request(chat_id: int, request_id: int, chat_history):
    db.update_request_status(request_id, "intent", "in work")
    await asyncio.sleep(1)
    intent = "test"
    db.update_request_status(request_id, "intent", "done")
    db.update_chat_summary_intent(chat_id, intent)

    await asyncio.sleep(1)
    short_summary = "это краткое саммари вопроса"
    db.update_chat_summary_short_summary(chat_id, short_summary)

    db.update_request_status(request_id, "emotion", "in work")
    await asyncio.sleep(1)
    emotion = "happy"
    db.update_request_status(request_id, "emotion", "done")
    db.update_request_emotion(request_id, emotion)
    db.update_chat_summary_emotion(chat_id, emotion)

    db.update_request_status(request_id, "knowledge", "in work")
    await asyncio.sleep(1)
    db.update_request_status(request_id, "knowledge", "done")

    db.update_request_status(request_id, "actions", "in work")
    await asyncio.sleep(1)
    actions = ["Добри день...", "Здравствути...", "Пока..."]
    db.update_request_status(request_id, "actions", "done")
    db.update_request_actions(request_id, actions)

    db.update_request_status(request_id, "quality", "in work")
    db.update_request_status(request_id, "summary", "in work")
    await asyncio.sleep(60)
    quality = "чел норм ответил, во класс"
    db.update_request_status(request_id, "quality", "done")
    db.update_chat_quality(chat_id, quality)
    await asyncio.sleep(1)
    crm = {
        "issue_type": "billing",
        "client_sentiment": "happy",
        "resolution": "info_provided",
    }
    db.update_request_status(request_id, "summary", "done")
    db.update_chat_crm(chat_id, crm)
