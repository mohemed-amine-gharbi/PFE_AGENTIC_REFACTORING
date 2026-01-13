# agents/llm_agent.py
from agents.base_agent import BaseAgent
from llm.llm_client import LLMClient

class LLMAgent(BaseAgent):
    def __init__(self, name):
        super().__init__(name)
        self.llm = LLMClient()

    def reason(self, prompt: str) -> str:
        return self.llm.ask(prompt)
