import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class ActionSuggestionAgent(BaseAgent):
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

    def _llm(verbose: bool):
        return ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_ACTIONSUGGESTION_AGENT", "qwen2.5-32b-instruct"),
            verbose=verbose,
        )

    def _tools():
        def lower_tool(query: str):
            return query.lower()

        tools = [
            Tool(
                name="lower",
                func=lower_tool,
                description="Возвращает текст строчными буквами",
            ),
        ]

        return tools
