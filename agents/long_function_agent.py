# agents/long_function_agent.py
import ast
from agents.llm_agent import LLMAgent

class LongFunctionAgent(LLMAgent):
    def __init__(self):
        super().__init__("Long Function Agent")

    def analyze(self, code):
        tree = ast.parse(code)
        long_funcs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if (node.end_lineno - node.lineno) > 20:
                    long_funcs.append(node.name)

        prompt = f"""
Ces fonctions sont trop longues : {long_funcs}
Propose un découpage logique en sous-fonctions.
Code :
{code}
"""
        return {
            "long_functions": long_funcs,
            "refactor": self.reason(prompt)
        }
