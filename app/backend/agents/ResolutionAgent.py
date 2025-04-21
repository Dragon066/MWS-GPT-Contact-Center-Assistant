import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class ResolutionAgent(BaseAgent):
    RESOLUTIONS = ["info_provided", "escalation", "compensation"]

    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_EMOTION_AGENT", "qwen2.5-32b-instruct"),
            temperature=0,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты — аналитик поддержки. Анализируй историю чата и определяй итоговое решение (resolution).",
                ),
                ("system", "Доступные решения:"),
                (
                    "system",
                    "1. info_provided - клиент получил нужную информацию, вопрос закрыт\n"
                    "2. escalation - требуется передача специалисту\n"
                    "3. compensation - необходимо предложить компенсацию",
                ),
                ("system", "Правила классификации:"),
                (
                    "system",
                    "1. Если в чате есть нерешенная проблема или конфликт - выбирай escalation",
                ),
                (
                    "system",
                    "2. Если клиент явно недоволен и требует возмещения - выбирай compensation",
                ),
                (
                    "system",
                    "3. Если вопрос полностью решен и клиент удовлетворен - выбирай info_provided",
                ),
                ("system", "Примеры:"),
                (
                    "system",
                    "Чат: 'Спасибо, всё понятно' -> info_provided",
                ),
                (
                    "system",
                    "Чат: 'Меня это не устраивает, хочу жалобу!' -> escalation",
                ),
                (
                    "system",
                    "Чат: 'Вы должны мне компенсировать убытки!' -> compensation",
                ),
                ("system", "Отвечай ТОЛЬКО одним словом из списка, без пояснений"),
                ("human", "{chat}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain
