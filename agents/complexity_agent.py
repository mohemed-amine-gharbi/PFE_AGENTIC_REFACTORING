import ast
from agents.base_agent import BaseAgent

class ComplexityAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("ComplexityAgent", llm)

    def analyze(self, code):
        tree = ast.parse(code)
        results = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = sum(
                    isinstance(n, (ast.If, ast.For, ast.While))
                    for n in ast.walk(node)
                )
                if complexity > 4:
                    results.append({
                        "function": node.name,
                        "complexity": complexity
                    })
        return results

    def build_prompt(self, analysis):
        return f"""
The following functions have high cyclomatic complexity:
{analysis}

Explain how to refactor them.
"""
