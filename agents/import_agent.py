# agents/import_agent.py
import ast
from agents.llm_agent import LLMAgent

class ImportAgent(LLMAgent):
    def __init__(self):
        super().__init__("Import Agent")

    def analyze(self, code):
        tree = ast.parse(code)
        imports = [ast.unparse(n) for n in ast.walk(tree)
                   if isinstance(n, (ast.Import, ast.ImportFrom))]

        prompt = f"""
Analyse les imports suivants et indique ceux qui sont inutiles ou dupliqués :
{imports}
"""
        return {
            "imports": imports,
            "analysis": self.reason(prompt)
        }
