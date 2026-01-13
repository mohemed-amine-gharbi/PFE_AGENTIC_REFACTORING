from agents.base_agent import BaseAgent
import ast

class RenameAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("RenameAgent", llm)

    def analyze(self, code):
        tree = ast.parse(code)
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Détecte les noms trop courts ou peu explicites
                if len(node.name) <= 2:
                    results.append(node.name)
        return results

    def build_prompt(self, analysis):
        return f"""
Detected poorly named functions:
{analysis}

Suggest more meaningful names.
"""
