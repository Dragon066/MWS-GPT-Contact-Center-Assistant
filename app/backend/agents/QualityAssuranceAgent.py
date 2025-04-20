import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class QualityAssuranceAgent(BaseAgent):
    def __new__(self, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_QUALITY_AGENT", "qwen2.5-32b-instruct"),
            temperature=0,
            verbose=verbose,
        )

        # Промпт для оценки качества общения
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты — агент по оценке качества общения оператора с клиентом. Проанализируй чат на соответствие стандартам общения.",
                ),
                (
                    "system",
                    "Оцени, соблюдаются ли следующие принципы: честность, уважение и профессионализм. Оцените, есть ли в общении оператора с клиентом элементы, которые могут быть расценены как неуважительные или недопустимые.",
                ),
                (
                    "system",
                    "Если в чате присутствуют какие-либо проблемы, предложи корректировки поведения оператора.",
                ),
                (
                    "system",
                    'Твоя задача - вывести сообщение "ОК", если ты считаешь, что всё соблюдено, или "КОРРЕКТИРОВКА: ...", если требуются какие-то корректирующие меры (максимально кратко их опиши - например, "быть дружелюбнее")',
                ),
                ("human", "{chat}"),
            ]
        )

        # Пайплайн для обработки с использованием LLM
        chain = prompt | llm | StrOutputParser()

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain
