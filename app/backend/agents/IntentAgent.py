import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class IntentAgent(BaseAgent):
    INTENTS = [
        "проблема с оплатой",
        "жалоба",
        "техническая проблема",
        "сопровождение информацией",
        "другое",
    ]

    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_INTENT_AGENT", "qwen2.5-32b-instruct"),
            temperature=0,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты — классификатор намерений пользователя. Твоя задача — определить основную тему сообщений пользователя.",
                ),
                (
                    "system",
                    f"Темы для классификации: {', '.join(cls.INTENTS)}.",
                ),
                (
                    "system",
                    "Пожалуйста, выбери только одну тему. Если несколько тем подходят, выбери наиболее очевидную.",
                ),
                (
                    "system",
                    "Если сообщение не имеет отношения к этим темам, выбери 'другое'.",
                ),
                (
                    "system",
                    "Помни, что сообщение может быть неполным, и тебе нужно делать выводы на основе имеющейся информации.",
                ),
                ("system", "Отвечай только одной темой из списка, без пояснений."),
                ("human", "{chat}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain
