import os
import warnings

import requests
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import Runnable
from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)


class KnowledgeAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_KNOWLEDGE_AGENT", "qwen2.5-32b-instruct"),
            verbose=verbose,
        )

        tools = cls._tools()

        system_prompt = """Ты экспертный помощник компании. ИСПОЛЬЗУЙ РУССКИЙ ЯЗЫК. Всегда сначала используй инструмент Vector Search 
        для поиска информации в базе знаний. Отвечай только на основе найденных данных. Если информации нет, 
        скажи об этом. Не выдумывай факты. Формат ответа: развёрнутый, но по делу. Если ты нашёл очень близкую информацию к твоему запросу
        - отвечай максимально приближенно к эталонному ответу из базы знаний."""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            agent_kwargs={"prompt": prompt},
        )

        return agent

    def _tools():
        def vector_search(query: str):
            try:
                r = requests.post(
                    "http://backend:8002/qdrantquery", json={"query": query}
                ).json()
                return str(r)
            except Exception as ex:
                return f"Возникла ошибка при запросе: {ex}"

        tools = [
            Tool(
                name="Vector Search",
                func=vector_search,
                description="Осуществляет поиск по базе знаний с помощью переданной строки query. Используй всегда. Передавай в аргументы что считаешь нужным. ИСПОЛЬЗУЙ РУССКИЙ ЯЗЫК",
            ),
        ]

        return tools
