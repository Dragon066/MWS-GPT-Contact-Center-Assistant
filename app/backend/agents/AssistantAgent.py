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


class AssistantAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_ASSISTANT_AGENT", "qwen2.5-32b-instruct"),
            temperature=0.2,
            verbose=verbose,
        )

        tools = cls._tools()

        system_prompt = """Ты профессиональный ассистент для оператора поддержки. Твои задачи:
1. Отвечай на ЛЮБЫЕ вопросы оператора, связанные с работой компании
2. Всегда сначала используй инструмент Vector Search для проверки информации
3. Формулируй точные ответы на основе данных из системы
4. Сохраняй профессиональный стиль общения

Правила:
- Отвечай только на русском языке
- Если информация не найдена - честно сообщи об этом
- Не выдумывай факты
- Для технических вопросов обязательно используй поиск в базе знаний
- Можешь отвечать на общие вопросы без использования инструментов
- Всегда сохраняй контекст диалога"""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Контекст диалога с клиентом:\n{chat_history}\n\nВопрос оператора: {input}",
                ),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
            agent_kwargs={"prompt": prompt, "memory": cls._create_memory()},
            handle_parsing_errors=True,
        )

        return agent

    @classmethod
    def _tools(cls):
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

    @classmethod
    def _create_memory(cls):
        from langchain.memory import ConversationBufferMemory

        return ConversationBufferMemory(
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            return_messages=True,
        )
