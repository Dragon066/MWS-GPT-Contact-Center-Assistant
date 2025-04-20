import os
from abc import ABC

from langchain.schema.runnable import Runnable


class BaseAgent(ABC):
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL")

    def __new__(cls, verbose: bool = False) -> Runnable: ...
