import asyncio
import os

from agents import (
    ActionSuggestionAgent,
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

    # Возвращаем новую Runnable с трекингом
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


async def push_record(chat_id: int, chat_history):
    if chat_history[-1]["role"] in ("human", "user"):
        request_id, is_new = db.add_new_request(chat_id, len(chat_history))
    else:
        request_id = db.get_last_request(chat_id)
        is_new = False
    if is_new:
        asyncio.create_task(process_request(chat_id, request_id, chat_history))
    return request_id


async def process_request(chat_id: int, request_id: int, chat_history):
    intent_agent_track = with_tracking(intent_agent, "intent", request_id)
    emotion_agent_track = with_tracking(emotion_agent, "emotion", request_id)
    knowledge_agent_track = with_tracking(knowledge_agent, "knowledge", request_id)
    summary_agent_track = with_tracking(summary_agent, "summary", request_id)
    action_agent_track = with_tracking(action_agent, "action", request_id)

    last_message = chat_history[-1]["content"]

    intent = await intent_agent_track.ainvoke(chat_history)
    db.update_chat_summary_intent(chat_id, intent)

    short_summary = await summary_agent_track.ainvoke(chat_history)
    db.update_chat_summary_short_summary(chat_id, short_summary)

    emotion_last = await emotion_agent_track.ainvoke(last_message)
    db.update_request_emotion(request_id, emotion_last)

    emotion_chat = await emotion_agent_track.ainvoke(chat_history)
    db.update_chat_summary_emotion(chat_id, emotion_chat)

    knowledge = await knowledge_agent_track.ainvoke(chat_history)

    actions = await action_agent_track.ainvoke(
        {
            "chat": chat_history,
            "knowledge": knowledge,
            "emotion": emotion_last,
            "intent": intent,
            "metadata": {"not": "provided"},
            "operator": {"name": "Алексей", "position": "Технический специалист"},
        }
    )
    db.update_request_actions(request_id, actions)


async def process_solved_chat(chat_id: int, chat_history):
    request_id = db.get_last_request(chat_id)

    summary_agent_track = with_tracking(summary_agent, "summary", request_id)
    quality_agent_track = with_tracking(quality_agent, "quality", request_id)
    resolution_agent_track = with_tracking(resolution_agent, "resolution", request_id)

    summary = await summary_agent_track.ainvoke(chat_history)
    db.update_chat_summary_intent(chat_id, summary)

    intent = "to add"
    emotion = "to add"

    quality = await quality_agent_track.ainvoke(chat_history)

    resolution = await resolution_agent_track.ainvoke(chat_history)

    crm = {
        "intent": intent,
        "emotion": emotion,
        "summary": summary,
        "quality": quality,
        "resolution": resolution,
    }

    print(crm)
