import io
import logging

import aiohttp
from core import llmquery, push_record, push_solved_chat
from db import Database
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
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


class ChatIdWithOperatorRequest(BaseModel):
    chat_id: int
    operator_name: str
    operator_position: str


@app.post("/push_request")
async def push_request(request: ChatIdWithOperatorRequest):
    chat_id = request.chat_id
    operator_name = request.operator_name
    operator_position = request.operator_position
    """Запушить запрос на обработку агентами и получить айди, по которому можно получить информацию обратно"""
    chat_history = await fetch_json(f"http://crm:8003/api/chat?id_chat={chat_id}")
    request_id = await push_record(
        chat_id, chat_history, operator_name, operator_position
    )
    return {"request_id": request_id}


class ChatIdRequest(BaseModel):
    chat_id: int


@app.post("/push_solved_record")
async def push_solved_record(request: ChatIdRequest):
    """Запушить решённый чат на обработку финальной цепочкой агентов и формирования CRM отчёта"""
    chat_id = request.chat_id
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


class LLMQueryRequest(BaseModel):
    query: str
    chat_id: int


@app.post("/llmquery")
async def process_llm_query(request: LLMQueryRequest):
    query = request.query
    chat_id = request.chat_id
    """Отправить запрос агенту-ассистенту (встроенный LLM чат)"""
    chat_history = await fetch_json(f"http://crm:8003/api/chat?id_chat={chat_id}")
    result = await llmquery(query, chat_history)
    return {"result": result}


class QueryRequest(BaseModel):
    query: str
    k: int = 3


@app.post("/qdrantquery")
async def qdrantquery(request: QueryRequest):
    """Отправить запрос в векторную базу данных и получить k релевантных результатов"""
    return get_topk_results("database", request.query, request.k)
