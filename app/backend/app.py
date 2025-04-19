import aiohttp
from core import push_record
from db import Database
from fastapi import FastAPI

app = FastAPI()

db = Database()


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


@app.get("/push_request")
async def push_request(chat_id: int):
    chat_history = await fetch_json(f"http://crm:8003/api/chat?id_chat={chat_id}")
    request_id = await push_record(chat_id, chat_history)
    return {"request_id": request_id}


@app.get("/get_request_info")
async def get_request_info(request_id: int):
    try:
        data = db.get_request_data(request_id)
    except Exception as ex:
        data = {"Error": ex}
    return data


@app.get("/get_chat_info")
async def get_chat_info(chat_id: int):
    try:
        data = db.get_chat_summary_data(chat_id)
    except Exception as ex:
        data = {"Error": ex}
    return data
