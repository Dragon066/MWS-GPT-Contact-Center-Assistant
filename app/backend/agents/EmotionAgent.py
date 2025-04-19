import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from BaseAgent import BaseAgent


# class EmotionAgent(BaseAgent):
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
#             model=os.getenv("LLM_EMOTION_AGENT", "qwen2.5-32b-instruct"),
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


class EmotionAgent(BaseAgent):
    def __init__(self, verbose: bool = False):
        self.llm = ChatOpenAI(
            base_url=os.getenv("LLM_BASE_URL"),
            api_key=os.getenv("LLM_API_KEY"),
            model=os.getenv("LLM_EMOTION_AGENT", "qwen2.5-32b-instruct"),
            temperature=0,
            verbose=verbose,
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Ты — классификатор эмоций. Анализируй текст и определяй ДОМИНИРУЮЩУЮ эмоцию.")
            ("system"," Если эмоция смешанная или неясная:")
            ("system", "1. Выбери наиболее выраженную")
            ("system", "2. Если одинаково - выбери первую по списку")
            ("system", "3. Для сарказма/иронии используй 'гнев' ")
            ("system", "Выбери одну из: гнев, радость, нейтральное, грусть, удивление. Отвечай только одним словом."),
            ("human", "{text}")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def invoke(self, input_text: str) -> str:
        return self.chain.invoke({"text": input_text})

