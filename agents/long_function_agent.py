from agents.base_agent import BaseAgent
import ast

class LongFunctionAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("LongFunctionAgent", llm)

    def analyze(self, code):
        tree = ast.parse(code)
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                lines = node.body
                if len(lines) > 10:  # fonction trop longue
                    results.append({
                        "function": node.name,
                        "lines": len(lines)
                    })
        return results

    def build_prompt(self, analysis):
        return f"""
Detected long functions:
{analysis}

Suggest a strategy to break them into smaller functions.
"""
