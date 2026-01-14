class LongFunctionAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, code):
        functions = []
        current = []
        for line in code.splitlines():
            if line.startswith("def "):
                if current:
                    functions.append(current)
                current = [line]
            elif current:
                current.append(line)
        if current:
            functions.append(current)

        return [f for f in functions if len(f) > 10]

    def prompt(self, analysis, code):
        if not analysis:
            return code

        return f"""
You are a Python refactoring agent.

Split long functions into smaller logical functions.
Return ONLY the refactored Python code.

CODE:
{code}
"""
