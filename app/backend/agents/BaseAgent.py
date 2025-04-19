import os
from abc import ABC


class BaseAgent(ABC):
    LLM_API_KEY: str = os.getenv("LLM_API_KEY")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL")

    def __new__(cls, verbose: bool = False): ...

    def _llm(verbose: bool): ...

    def _tools(): ...
