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


async def get_record(id_chat):
    return db.get_record(id_chat)


@router.get("/records")
async def get_records_api(id_chat: int | None = None):
    """Получить все чаты при id_chat = None и получить конкретный Record при id_chat: integer"""
    if id_chat is None:
        return await get_all_records()
    return await get_record(id_chat)


async def get_chat(id_chat):
    return db.get_all_messages(id_chat)


@router.get("/chat")
async def get_chat_api(id_chat: int):
    """Получить все сообщения из чата"""
    return await get_chat(id_chat)


async def mark_as_solved(id_chat):
    return db.mark_as_solved(id_chat)


class ChatIdRequest(BaseModel):
    id_chat: int


@router.post("/mark_as_solved")
async def mark_as_solved_api(request: ChatIdRequest):
    """Пометить чат как решённый"""
    return await mark_as_solved(request.id_chat)


class CRMRequest(BaseModel):
    id_chat: int
    summary: dict


@router.post("/push_crm_summary")
async def push_crm_summary_api(request: CRMRequest):
    """Запушить отчёт в систему"""
    id_chat = request.id_chat
    summary = request.summary
    return db.push_crm_summary(id_chat, summary)


async def get_last_chat_messages():
    return db.get_last_chat_messages()
