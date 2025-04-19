import os

from langchain.agents import AgentExecutor, AgentType, Tool, initialize_agent
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class EmotionAgent(BaseAgent):
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
            model=os.getenv("LLM_EMOTION_AGENT", "qwen2.5-32b-instruct"),
            verbose=verbose,
        )

    def _tools():

        # def lower_tool(query: str):
        #     return query.lower()

        # tools = [
        #     Tool(
        #         name="lower",
        #         func=lower_tool,
        #         description="Возвращает текст строчными буквами",
        #     ),
        # ]

        # return tools
        def classify_emotion(query: str):
            prompt = f"""Ты — эксперт по анализу эмоций в тексте. Твоя задача — классифицировать эмоциональную окраску текста на русском языке.  
            Варианты: 1. Гнев 2. Радость 3. Печаль 4. Удивление 5. Нейтральное"""

        tools = [
            Tool(
                name="lower",
                func=classify_emotion,
                description="Распознает одну из эмоций. Предварительно: 'гнев', 'радость', 'печаль', 'тоска', 'удивление', 'нейтральное'",
            ),
        ]