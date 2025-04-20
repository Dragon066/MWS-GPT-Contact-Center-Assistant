import ast
import os
from typing import Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class PythonListOutputParser(StrOutputParser):
    def parse(self, text: str) -> List[Dict]:
        try:
            # Извлекаем список из текста ответа
            start = text.find("[")
            end = text.rfind("]") + 1
            return ast.literal_eval(text[start:end])
        except (SyntaxError, ValueError):
            return []  # Возвращаем пустой список при ошибке парсинга


class ActionSuggestionAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_ACTION_AGENT", "qwen2.5-32b-instruct"),
            temperature=0.3,  # Немного креативности
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Ты — AI-ассистент оператора поддержки. Сгенерируй 2-3 действия для оператора на основе:
                - История чата: {chat}
                - Ответ из базы знаний: {knowledge}
                - Эмоция клиента: {emotion}
                - Тема чата: {intent}
                - Метаданные клиента: {metadata}
                - Информация об операторе: {operator}

                Формат ответа ТОЛЬКО как Python-список словарей:
                actions = [{{"title": "Заголовок", "text": "Описание", "type": "тип"}}, ...]

                Возможные типы действий:
                - help: Предложение помощи/решения
                - compensation: Компенсация/бонусы
                - escalation: Эскалация проблемы
                - greeting: Приветствие/прощание
                
                Заголовок не должен превышать 2-3 слов.
                
                Одним из действий может быть ответ из базы знаний. ОТВЕЧАЙ НА РУССКОМ ЯЗЫКЕ.
                
                Все действия являются взаимоисключающими - оператор может выбрать только одно из них, учти это. 
                Предлагай компенсацию пользователю, если долго не удаётся решить проблему.
                
                Приветствуй пользователя от лица оператора, если это первое его сообщение.
                Сопровождай ответы запросом обратной связи при необходимости.

                Пример:
                actions = [
                    {{"title": "Решение проблемы", 
                    "text": "Для решения вашей проблемы попробуйте...", 
                    "type": "help"}},
                    {{"title": "Компенсация",
                    "text": "В качестве извинений предлагаем...",
                    "type": "compensation"}}
                ]""",
                )
            ]
        )

        chain = prompt | llm | PythonListOutputParser()

        return chain
