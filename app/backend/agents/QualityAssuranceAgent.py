import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class QualityAssuranceAgent(BaseAgent):
    RULES = "Всегда приветствуйте клиента вежливо, говорите четко и просто, проявляйте эмпатию, уточняйте детали, действуйте быстро по инструкции, сохраняйте спокойствие при любом тоне клиента, завершайте диалог подтверждением решения вопроса и доброжелательным прощанием – оператор представляет компанию, его речь влияет на репутацию."

    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_QUALITY_AGENT", "qwen2.5-32b-instruct"),
            temperature=0,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты — агент по оценке качества общения оператора с клиентом. Проанализируй чат на соответствие стандартам общения ниже. ОТВЕЧАЙ НА РУССКОМ ЯЗЫКЕ.",
                ),
                (
                    "system",
                    f"СТАНДАРТЫ ОБЩЕНИЯ КОМПАНИИ: {cls.RULES}",
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

        chain = prompt | llm | StrOutputParser()

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain
