import os

import requests
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.schema.runnable import Runnable
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class KnowledgeAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_KNOWLEDGE_AGENT", "qwen2.5-32b-instruct"),
            verbose=verbose,
        )

        tools = cls._tools()

        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
        )

        return agent

    def _tools():
        def vector_search(query: str):
            try:
                r = requests.get(
                    f"http://backend:8002/qdrantquery?query={query}"
                ).json()
                return r
            except Exception as ex:
                return f"Возникла ошибка при запросе: {ex}"

        tools = [
            Tool(
                name="Vector Search",
                func=vector_search,
                description="Осуществляет поиск по базе знаний с помощью переданной строки query. Используй всегда. Передавать в аргумент без изменений.",
            ),
        ]

        return tools
