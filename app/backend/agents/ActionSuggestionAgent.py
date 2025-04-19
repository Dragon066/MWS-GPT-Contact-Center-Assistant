import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from BaseAgent import BaseAgent


# class ActionSuggestionAgent(BaseAgent):
#     def __new__(cls, verbose: bool = False) -> AgentExecutor:
#         llm = cls._llm(verbose)
#         tools = cls._tools()
#         agent = initialize_agent(
#             tools,
#             llm,
#             agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#             verbose=verbose,
#         )
#         return agent

#     def _llm(verbose: bool):
#         return ChatOpenAI(
#             base_url=BaseAgent.LLM_BASE_URL,
#             api_key=BaseAgent.LLM_API_KEY,
#             model=os.getenv("LLM_ACTIONSUGGESTION_AGENT", "qwen2.5-32b-instruct"),
#             verbose=verbose,
#         )

#     def _tools():
#         def lower_tool(query: str):
#             return query.lower()

#         tools = [
#             Tool(
#                 name="lower",
#                 func=lower_tool,
#                 description="Возвращает текст строчными буквами",
#             ),
#         ]

#         return tools

class ActionSuggestionAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        self.llm = ChatOpenAI(
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY"),
            model="qwen2.5-32b-instruct",
            temperature=0.3,
            verbose=verbose,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Ты — агент предложения действий в CRM. Всегда отвечай в формате:
            Thought: <анализ контекста, эмоции и намерения>
            Action: <конкретное действие или шаг>
            Answer: <готовый текст для оператора или клиента>"""),

            #с примером еще подумать надо
            # ("system", """Пример:
            # Thought: Клиент раздражен (гнев), намерение — прекращение пользования услугами нашей компании. Контекст: политика возвратов позволяет предложить компенсацию.
            # Action: Предложить скидку 10% и извиниться.
            # Answer: "Извините за задержку! В качестве компенсации предлагаем скидку 10% на следующий заказ."""),

            ("human", """Эмоция: {emotion}
            Намерение: {intent}
            Контекст: {context}
            Запрос пользователя: "{text}" """)
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def invoke(self, text: str, emotion: str, intent: str, context: str) -> str:
        return self.chain.invoke({
            "text": text,
            "emotion": emotion,
            "intent": intent,
            "context": context
        })