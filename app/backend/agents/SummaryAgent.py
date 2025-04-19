import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


# class SummaryAgent(BaseAgent):
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
#             model=os.getenv("LLM_SUMMARY_AGENT", "qwen2.5-32b-instruct"),
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
class SummaryAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> AgentExecutor:
        llm = cls._llm(verbose)
        tools = cls._tools()
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=verbose,
        )
        return agent

    @staticmethod
    def _llm(verbose: bool):
        return ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_SUMMARY_AGENT", "qwen2.5-32b-instruct"),
            verbose=verbose,
        )

    @staticmethod
    def _tools():
        # A tool to generate a summary of the conversation
        def summarize_tool(conversation: str) -> str:
            summary_prompt = f"Сформируй краткое резюме диалога для автозаполнения CRM: {conversation}"
            return summary_prompt

        # The 'summarize' tool uses the 'summarize_tool' function
        tools = [
            Tool(
                name="summarize",
                func=summarize_tool,
                description="Сформулирует краткое резюме для автозаполнения CRM."
            ),
        ]
        return tools
