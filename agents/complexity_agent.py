# agents/complexity_agent.py
from radon.complexity import cc_visit
from agents.llm_agent import LLMAgent

class ComplexityAgent(LLMAgent):
    def __init__(self):
        super().__init__("Complexity Agent")

    def analyze(self, code):
        complex_funcs = [
            r.name for r in cc_visit(code) if r.complexity > 10
        ]

        prompt = f"""
Les fonctions suivantes ont une forte complexité cyclomatique :
{complex_funcs}
Explique le problème et propose une simplification.
Code :
{code}
"""
        return {
            "complex_functions": complex_funcs,
            "suggestions": self.reason(prompt)
        }
