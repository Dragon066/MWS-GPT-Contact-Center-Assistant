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
            start = text.find("[")
            end = text.rfind("]") + 1
            return ast.literal_eval(text[start:end])
        except (SyntaxError, ValueError):
            return []


class ActionSuggestionAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_ACTION_AGENT", "qwen2.5-32b-instruct"),
            temperature=0.2,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Ты — оператор контакт-центра с именем и должностью: {operator}. 
                Твоя задача сгенерировать 1-3 действия для оператора на основе:
                - История чата: {chat}
                - Готовый ответ из базы знаний: {knowledge}
                - Эмоция клиента: {emotion}
                - Тема чата: {intent}
                - Метаданные клиента: {metadata}

                Формат ответа ТОЛЬКО как Python-список словарей:
                actions = [{{"title": "Заголовок", "text": "Описание"}}, ...]
                
                ## Требования к ответу:
                1. Возможные типы действий:
                - Предложение помощи/решения (из базы знаний!)
                - Компенсация/бонусы (только в крайнем случае!)
                - Эскалация проблемы
                
                2. Заголовок не должен превышать 2-3 слов.
                
                3. Одним из действий может быть ответ из базы знаний. ОТВЕЧАЙ НА РУССКОМ ЯЗЫКЕ.
                
                4. Предлагай компенсацию пользователю, если долго не удаётся решить проблему.
                
                5. Для новых чатов (первое сообщение клиента):
               - Добавляй приветствие в виде "Здравствуйте! На связи _position_ _name_"
               - Предлагай помощь в дружелюбной форме
                
                6. Сопровождай КАЖДОЕ действие запросом обратной связи при необходимости.
                
                7. Текст ОБЯЗАН быть отформатирован в Markdown формате ОБЯЗАТЕЛЬНО С ДВОЙНЫМ переносом строк.

                Пример:
                actions = [
                    {{"title": "Решение проблемы", 
                    "text": "Для решения вашей проблемы попробуйте..."}},
                    {{"title": "Компенсация",
                    "text": "В качестве извинений предлагаем..."}}
                ]""",
                )
            ]
        )

        chain = prompt | llm | PythonListOutputParser()

        return chain
