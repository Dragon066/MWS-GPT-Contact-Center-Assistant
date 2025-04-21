import io
import logging

import aiohttp
from core import llmquery, push_record, push_solved_chat
from db import Database
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.openapi.docs import get_swagger_ui_html
from qdrant import (
    create_collection_from_file,
    get_collection,
    get_topk_results,
    is_collection_exists,
)

app = FastAPI(openapi_url="/docs/openapi.json", docs_url=None, redoc_url=None)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/llmapi" + app.openapi_url,
        title="Backend API Docs",
    )


db = Database()

logging.getLogger("uvicorn.access").addFilter(
    lambda record: "/get_chat_info" not in record.getMessage()
)
logging.getLogger("uvicorn.access").addFilter(
    lambda record: "/get_request_info" not in record.getMessage()
)


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


@app.get("/push_request")
async def push_request(chat_id: int, operatorName: str, operatorPosition: str):
    """Запушить запрос на обработку агентами и получить айди, по которому можно получить информацию обратно"""
    chat_history = await fetch_json(f"http://crm:8003/api/chat?id_chat={chat_id}")
    request_id = await push_record(
        chat_id, chat_history, operatorName, operatorPosition
    )
    return {"request_id": request_id}


@app.get("/push_solved_record")
async def push_solved_record(chat_id: int):
    """Запушить решённый чат на обработку финальной цепочкой агентов и формирования CRM отчёта"""
    chat_history = await fetch_json(f"http://crm:8003/api/chat?id_chat={chat_id}")
    request_id = await push_solved_chat(chat_id, chat_history)
    return {"request_id": request_id}


@app.get("/get_request_info")
async def get_request_info(request_id: int):
    """Получение информации по запросу"""
    try:
        data = db.get_request_data(request_id)
    except Exception as ex:
        data = {"error": str(ex)}
    return data


@app.get("/get_chat_info")
async def get_chat_info(chat_id: int):
    """Получение информации о чате в общем (создаётся автоматически при первом request)"""
    try:
        data = db.get_chat_summary_data(chat_id)
    except Exception as ex:
        data = {"error": str(ex)}
    return data


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Загрузка кастомной базы знаний"""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Поддерживаются только CSV файлы")

    contents = await file.read()

    await create_collection_from_file("database", io.StringIO(contents.decode("utf-8")))

    return {
        "status": "success",
        "message": "File uploaded successfully",
    }


@app.get("/collection_size")
async def get_collection_size():
    """Получение информации о существующей базе знаний"""
    if is_collection_exists("database"):
        return {"points_count": get_collection("database").points_count}
    else:
        return {"error": "no collection"}


@app.get("/llmquery")
async def process_llm_query(query: str, chat_id: int):
    """Отправить запрос агенту-ассистенту (встроенный LLM чат)"""
    chat_history = await fetch_json(f"http://crm:8003/api/chat?id_chat={chat_id}")
    result = await llmquery(query, chat_history)
    return {"result": result}


@app.get("/qdrantquery")
async def qdrantquery(query: str, k: int = 3):
    """Отправить запрос в векторную базу данных и получить k релевантных результатов"""
    return get_topk_results("database", query, k)
