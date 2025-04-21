from db import Database
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api")

db = Database()


@router.get("/push_record")
async def push_record(
    id: int,
    type: str,
    content: str,
    role: str = "user",
):
    """Запушить новое сообщение (id=chat_id)
    Создаст новую запись, если до этого не было"""
    db.add_data(id, type, content, role)
    return {"status": "success"}


async def get_all_records():
    return db.get_all_records()


async def get_record(chat_id):
    return db.get_record(chat_id)


@router.get("/records")
async def get_records_api(chat_id: int | None = None):
    """Получить все чаты при chat_id = None и получить конкретный Record при chat_id: integer"""
    if chat_id is None:
        return await get_all_records()
    return await get_record(chat_id)


async def get_chat(chat_id):
    return db.get_all_messages(chat_id)


@router.get("/chat")
async def get_chat_api(chat_id: int):
    """Получить все сообщения из чата"""
    return await get_chat(chat_id)


async def mark_as_solved(chat_id):
    return db.mark_as_solved(chat_id)


class ChatIdRequest(BaseModel):
    chat_id: int


@router.post("/mark_as_solved")
async def mark_as_solved_api(request: ChatIdRequest):
    """Пометить чат как решённый"""
    return await mark_as_solved(request.chat_id)


class CRMRequest(BaseModel):
    chat_id: int
    summary: dict


@router.post("/push_crm_summary")
async def push_crm_summary_api(request: CRMRequest):
    """Запушить отчёт в систему"""
    chat_id = request.chat_id
    summary = request.summary
    return db.push_crm_summary(chat_id, summary)


async def get_last_chat_messages():
    return db.get_last_chat_messages()
