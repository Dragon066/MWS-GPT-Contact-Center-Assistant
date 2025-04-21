from urllib.parse import quote_plus

from crm_api import get_all_records, get_last_chat_messages, router
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.templating import Jinja2Templates

app = FastAPI(openapi_url="/docs/openapi.json", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")
app.include_router(router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/crm" + app.openapi_url,
        title="CRM API Docs",
    )


# Добавляем фильтры в Jinja2
def urlencode_filter(s):
    return quote_plus(str(s))


def truncate_filter(s, length=50):
    if len(s) > length:
        return s[:length] + "..."
    return s


templates.env.filters["urlencode"] = urlencode_filter
templates.env.filters["truncate"] = truncate_filter


@app.get("/")
async def root(request: Request):
    """Главная страница CRM-системы"""
    records = await get_all_records()
    latest_chats = await get_last_chat_messages()
    latest_chats = {chat.record_id: chat for chat in latest_chats}
    return templates.TemplateResponse(
        "data_records.html",
        {"request": request, "records": records, "latest_chats": latest_chats},
    )


@app.get("/emulator")
async def show_emulator_form(request: Request):
    """Страница эмулятора CRM-системы"""
    return templates.TemplateResponse("emulator_form.html", {"request": request})
