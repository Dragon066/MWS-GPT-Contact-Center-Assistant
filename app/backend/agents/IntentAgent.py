import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from BaseAgent import BaseAgent
# class IntentAgent(BaseAgent):
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
#             model=os.getenv("LLM_INTENT_AGENT", "qwen2.5-32b-instruct"),
#             verbose=verbose,
#         )

#     def _tools():
#         def classify_intent(query: str):
#             prompt = f"Возможные намерения: 'запрос на информацию', 'жалоба', 'вопрос', 'пожелание', 'техническая проблема', 'запрос на помощь'."
#             return prompt

#         tools = [
#             Tool(
#                 name="classify_intent",
#                 func=classify_intent,
#                 description="Классифицирует намерение пользователя в запросе на русском языке.",
#             ),
#         ]

#         return tools
class IntentAgent(BaseAgent):
    def __new__(cls, verbose: bool = False):
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model="qwen2.5-32b-instruct",  
            temperature=0,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты выбираешь наиболее подходящую тему для сообщения пользователя."),
            ("system", "Темы: 'проблема с оплатой', 'жалоба', 'техническая проблема', 'вопрос по заказу', 'другое'."),
            ("system", "Отвечай только одной темой из списка, без пояснений."),
            ("human", "{text}")
        ])

        chain = prompt | llm | StrOutputParser()
        return chain