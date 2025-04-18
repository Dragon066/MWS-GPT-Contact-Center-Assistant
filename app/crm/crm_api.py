from db import Database
from fastapi import APIRouter

router = APIRouter(prefix="/api")

db = Database()


@router.get("/push_record")
async def push_record(
    id: int,
    type: str,
    content: str,
    role: str = "user",
):
    db.add_data(id, type, content, role)
    return {"status": "success"}


async def get_records():
    return db.get_all_records()


@router.get("/records")
async def get_records_api():
    return await get_records()


async def get_chat(id_chat):
    return db.get_all_messages(id_chat)


@router.get("/chat")
async def get_chat_api(id_chat: int):
    return await get_chat(id_chat)


async def mark_as_solved(id_chat):
    return db.mark_as_solved(id_chat)


@router.get("/mark_as_solved")
async def mark_as_solved_api(id_chat: int):
    return await mark_as_solved(id_chat)


async def get_last_chat_messages():
    return db.get_last_chat_messages()
