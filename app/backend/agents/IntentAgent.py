import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class IntentAgent(BaseAgent):
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
            model=os.getenv("LLM_INTENT_AGENT", "qwen2.5-32b-instruct"),
            verbose=verbose,
        )

    def _tools():
        def classify_intent(query: str):
            prompt = f"Определи намерение пользователя в следующем запросе на русском языке: '{query}'. Возможные намерения: 'запрос на информацию', 'жалоба', 'вопрос', 'пожелание', 'техническая проблема', 'запрос на помощь'."
            return prompt

        tools = [
            Tool(
                name="classify_intent",
                func=classify_intent,
                description="Классифицирует намерение пользователя в запросе на русском языке.",
            ),
        ]

        return tools
