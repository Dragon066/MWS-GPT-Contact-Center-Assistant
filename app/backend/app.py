import asyncio
import io

import aiohttp
from core import push_record
from db import Database
from fastapi import FastAPI, File, HTTPException, UploadFile
from qdrant import create_collection_from_file, get_collection, is_collection_exists

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
        data = {"error": str(ex)}
    return data


@app.get("/get_chat_info")
async def get_chat_info(chat_id: int):
    try:
        data = db.get_chat_summary_data(chat_id)
    except Exception as ex:
        data = {"error": str(ex)}
    return data


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Поддерживаются только CSV файлы")

    # try:
    contents = await file.read()

    await create_collection_from_file("database", io.StringIO(contents.decode("utf-8")))

    return {
        "status": "success",
        "message": "File uploaded successfully",
    }
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


@app.get("/collection_size")
async def get_collection_size():
    if is_collection_exists("database"):
        return {"points_count": get_collection("database").points_count}
    else:
        return {"error": "no collection"}


@app.get("/llmquery")
async def process_llm_query(query: str, chat_id: int):
    await asyncio.sleep(2)
    return {"result": f"был получен запрос: {query}"}
