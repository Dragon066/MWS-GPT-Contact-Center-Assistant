import asyncio
import os

import aiohttp
from agents import (
    ActionSuggestionAgent,
    AssistantAgent,
    EmotionAgent,
    IntentAgent,
    KnowledgeAgent,
    QualityAssuranceAgent,
    ResolutionAgent,
    SummaryAgent,
)
from db import Database
from langchain.schema.runnable import RunnableLambda

db = Database()


def with_tracking(base_runnable, agent_name: str, request_id: str):
    async def track(input_data):
        db.update_request_status(request_id, agent_name, "in work")

        result = await base_runnable.ainvoke(input_data)

        db.update_request_status(request_id, agent_name, "done")

        return result

    return RunnableLambda(track)


VERBOSE_MODELS_AGENTS = os.getenv("VERBOSE_MODELS_AGENTS", True)
VERBOSE_MODELS_CHAINS = os.getenv("VERBOSE_MODELS_CHAINS", True)

intent_agent = IntentAgent(VERBOSE_MODELS_CHAINS)
emotion_agent = EmotionAgent(VERBOSE_MODELS_CHAINS)
knowledge_agent = KnowledgeAgent(VERBOSE_MODELS_AGENTS)
summary_agent = SummaryAgent(VERBOSE_MODELS_CHAINS)
quality_agent = QualityAssuranceAgent(VERBOSE_MODELS_CHAINS)
action_agent = ActionSuggestionAgent(VERBOSE_MODELS_CHAINS)
resolution_agent = ResolutionAgent(VERBOSE_MODELS_CHAINS)
assistant_agent = AssistantAgent(VERBOSE_MODELS_AGENTS)


async def push_record(chat_id: int, chat_history, operator_name, operator_position):
    if chat_history[-1]["role"] in ("human", "user"):
        request_id, is_new = db.add_new_request(chat_id, len(chat_history))
    else:
        request_id = db.get_last_request(chat_id)
        is_new = False
    if is_new:
        asyncio.create_task(
            process_request(
                chat_id, request_id, chat_history, operator_name, operator_position
            )
        )
    return request_id


async def push_solved_chat(chat_id: int, chat_history):
    request_id = db.get_last_request(chat_id)
    asyncio.create_task(process_solved_chat(chat_id, request_id, chat_history))
    return request_id


async def process_request(
    chat_id: int, request_id: int, chat_history, operator_name, operator_position
):
    intent_agent_track = with_tracking(intent_agent, "intent", request_id)
    emotion_agent_track = with_tracking(emotion_agent, "emotion", request_id)
    knowledge_agent_track = with_tracking(knowledge_agent, "knowledge", request_id)
    summary_agent_track = with_tracking(summary_agent, "summary", request_id)
    action_agent_track = with_tracking(action_agent, "action", request_id)

    db.update_request_status(request_id, "intent", "off")
    db.update_request_status(request_id, "emotion", "off")
    db.update_request_status(request_id, "knowledge", "off")
    db.update_request_status(request_id, "summary", "off")
    db.update_request_status(request_id, "action", "off")

    last_message = chat_history[-1]["content"]

    async def get_intent():
        intent = await intent_agent_track.ainvoke(chat_history)
        db.update_chat_summary_intent(chat_id, intent)
        return intent

    async def get_summary():
        short_summary = await summary_agent_track.ainvoke(chat_history)
        db.update_chat_summary_short_summary(chat_id, short_summary)
        return short_summary

    async def get_emotion_last():
        emotion_last = await emotion_agent_track.ainvoke(last_message)
        db.update_request_emotion(request_id, emotion_last)
        return emotion_last

    async def get_emotion_chat():
        emotion_chat = await emotion_agent_track.ainvoke(chat_history)
        db.update_chat_summary_emotion(chat_id, emotion_chat)
        return emotion_chat

    async def get_knowledge():
        return await knowledge_agent_track.ainvoke(chat_history)

    async def get_metadata():
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://crm:8003/api/records", params={"chat_id": chat_id}
            ) as response:
                return (await response.json())["client_meta"]

    (
        intent,
        short_summary,
        emotion_last,
        emotion_chat,
        knowledge,
        metadata,
    ) = await asyncio.gather(
        get_intent(),
        get_summary(),
        get_emotion_last(),
        get_emotion_chat(),
        get_knowledge(),
        get_metadata(),
    )

    async def execute_action():
        actions = await action_agent_track.ainvoke(
            {
                "chat": chat_history,
                "knowledge": knowledge,
                "emotion": emotion_last,
                "intent": intent,
                "metadata": metadata,
                "operator": {"name": operator_name, "position": operator_position},
            }
        )
        db.update_request_actions(request_id, actions)

    async def send_crm():
        crm_data = {
            "intent": intent,
            "emotion": emotion_chat,
            "summary": short_summary,
        }
        async with aiohttp.ClientSession() as session:
            await session.post(
                "http://crm:8003/api/push_crm_summary",
                json={"chat_id": chat_id, "summary": crm_data},
            )

    await asyncio.gather(execute_action(), send_crm())


async def process_solved_chat(chat_id: int, request_id: int, chat_history):
    summary_agent_track = with_tracking(summary_agent, "summary", request_id)
    quality_agent_track = with_tracking(quality_agent, "quality", request_id)
    resolution_agent_track = with_tracking(resolution_agent, "resolution", request_id)

    db.update_request_status(request_id, "summary", "off")
    db.update_request_status(request_id, "quality", "off")
    db.update_request_status(request_id, "resolution", "off")

    data = db.get_chat_summary_data(chat_id)
    intent = data.intent
    emotion = data.emotion_summary

    async def get_summary():
        summary = await summary_agent_track.ainvoke(chat_history)
        db.update_chat_summary_short_summary(chat_id, summary)
        return summary

    async def get_quality():
        return await quality_agent_track.ainvoke(chat_history)

    async def get_resolution():
        return await resolution_agent_track.ainvoke(chat_history)

    summary, quality, resolution = await asyncio.gather(
        get_summary(), get_quality(), get_resolution()
    )

    async def send_crm():
        crm_data = {
            "intent": intent,
            "emotion": emotion,
            "summary": summary,
            "quality": quality,
            "resolution": resolution,
        }
        async with aiohttp.ClientSession() as session:
            await session.post(
                "http://crm:8003/api/push_crm_summary",
                json={"chat_id": chat_id, "summary": crm_data},
            )

    await send_crm()


async def llmquery(query: str, chat_history):
    result = await assistant_agent.ainvoke(f"{chat_history} | ВОПРОС: {query}")
    return result["output"]
