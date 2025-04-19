import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from BaseAgent import BaseAgent

# class KnowledgeAgent(BaseAgent):
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
#             model=os.getenv("LLM_KNOWLEDGE_AGENT", "qwen2.5-32b-instruct"),
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


class FakeVectorDB:
    def __init__(self):
        # заглушка, потом будет Qdrant
        self.db = {
            "платежи": "Информация о процессах оплаты и подписке.",
            "поручения": "Процесс выполнения и отслеживания поручений.",
            "технические проблемы": "Общие инструкции по решению технических проблем.",
            "возврат": "Процедуры возврата товаров и услуг.",
        }

    def query(self, query: str):
        for key, value in self.db.items():
            if key in query.lower():
                return value
        return "Не удалось найти информацию по запросу."

class KnowledgeAgent(BaseAgent):
    def __new__(cls, verbose: bool = False):
        # Создаем LLM
        llm = ChatOpenAI(
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY"),
            model="qwen2.5-32b-instruct", 
            temperature=0,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты агент, который ищет информацию в базе знаний."),
            ("human", "{text}")
        ])

        # Создаем эмулатор работы с векторной БД
        fake_db = FakeVectorDB()

        def query_db(query: str):
            # Здесь будет интеграция с Qdrant в реальной версии
            return fake_db.query(query)

        # Связываем всё в цепочку
        chain = prompt | llm | StrOutputParser()

        # Возвращаем цепочку
        return chain, query_db