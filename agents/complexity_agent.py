class ComplexityAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, code):
        return [line for line in code.splitlines() if line.strip().startswith("if")]

    def prompt(self, analysis, code):
        if len(analysis) < 2:
            return code

        return f"""
You are a Python refactoring agent.

Reduce cyclomatic complexity by refactoring nested conditions
into helper functions.
Return ONLY the refactored Python code.

CODE:
{code}
"""
