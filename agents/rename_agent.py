# agents/rename_agent.py
import ast
from agents.llm_agent import LLMAgent

class RenameAgent(LLMAgent):
    def __init__(self):
        super().__init__("Rename Agent")

    def analyze(self, code):
        tree = ast.parse(code)
        bad_names = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and len(node.name) <= 2:
                bad_names.append(node.name)

        prompt = f"""
Tu es un expert en refactoring Python.
Propose des noms clairs pour ces fonctions : {bad_names}
Code :
{code}
"""
        return {
            "bad_names": bad_names,
            "suggestions": self.reason(prompt)
        }
