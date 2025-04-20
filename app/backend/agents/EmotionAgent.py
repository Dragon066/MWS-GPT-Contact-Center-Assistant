import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class EmotionAgent(BaseAgent):
    EMOTIONS = ["гнев", "радость", "нейтральное", "грусть", "удивление"]

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
                    "Ты — классификатор эмоций. Анализируй текст и определяй ДОМИНИРУЮЩУЮ эмоцию.",
                ),
                ("system", "Правила классификации:"),
                ("system", "1. Для смешанных эмоций выбирай наиболее выраженную"),
                (
                    "system",
                    "2. При равной выраженности выбирай первую из списка: "
                    + ", ".join(cls.EMOTIONS),
                ),
                ("system", "3. Сарказм/иронию классифицируй как 'гнев'"),
                ("system", "4. Отвечай ТОЛЬКО одним словом из списка, без пояснений"),
                ("system", "Примеры:"),
                (
                    "system",
                    "Вход: 'Я в восторге от вашего сервиса!' -> Выход: 'радость'",
                ),
                ("system", "Вход: 'Это просто ужасно!' -> Выход: 'гнев'"),
                ("human", "{text}"),
            ]
        )

        chain = (
            prompt
            | llm
            | StrOutputParser()
            | RunnableLambda(lambda x: cls.validate_emotion(x, cls.EMOTIONS))
        )

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain

    @staticmethod
    def validate_emotion(emotion: str, available_emotions: list[str]) -> str:
        emotion = emotion.strip().lower()
        return emotion if emotion in available_emotions else "нейтральное"
