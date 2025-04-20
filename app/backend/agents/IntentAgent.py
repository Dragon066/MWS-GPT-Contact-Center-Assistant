import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class IntentAgent(BaseAgent):
    def __new__(self, verbose: bool = False) -> Runnable:
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
                    "Ты — классификатор намерений пользователя. Твоя задача — определить основную тему сообщения пользователя.",
                ),
                (
                    "system",
                    "Темы для классификации: 'проблема с оплатой', 'жалоба', 'техническая проблема', 'вопрос по заказу', 'другое'.",
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
                ("human", "{text}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain
