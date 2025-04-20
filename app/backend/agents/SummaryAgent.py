import os

from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from .BaseAgent import BaseAgent


class SummaryAgent(BaseAgent):
    def __new__(cls, verbose: bool = False) -> Runnable:
        llm = ChatOpenAI(
            base_url=BaseAgent.LLM_BASE_URL,
            api_key=BaseAgent.LLM_API_KEY,
            model=os.getenv("LLM_SUMMARY_AGENT", "qwen2.5-32b-instruct"),
            temperature=0,
            verbose=verbose,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Ты — агент, который создает итоговое резюме для чатов. На основе диалога сформируй КРАТКОЕ РЕЗЮМЕ только по факту происходящего в чате.",
                ),
                ("human", "{chat}"),
            ]
        )

        chain = prompt | llm | StrOutputParser()

        if verbose:
            return chain.with_config({"callbacks": [ConsoleCallbackHandler()]})

        return chain
