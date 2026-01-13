from agents.base_agent import BaseAgent
import ast

class ImportAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("ImportAgent", llm)

    def analyze(self, code):
        tree = ast.parse(code)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def build_prompt(self, analysis):
        return f"""
Detected imports in the code:
{analysis}

Suggest which imports are unnecessary or could be simplified.
"""
