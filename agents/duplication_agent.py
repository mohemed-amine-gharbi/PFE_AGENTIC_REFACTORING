# agents/duplication_agent.py
from agents.llm_agent import LLMAgent

class DuplicationAgent(LLMAgent):
    def __init__(self):
        super().__init__("Duplication Agent")

    def analyze(self, code):
        prompt = f"""
Détecte toute duplication logique dans ce code Python.
Explique le problème et propose une factorisation.
Code :
{code}
"""
        return {
            "duplication_analysis": self.reason(prompt)
        }
