class DuplicationAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, code):
        lines = code.splitlines()
        duplicated_blocks = []
        seen = set()
        for line in lines:
            if line.strip() and line in seen:
                duplicated_blocks.append(line)
            seen.add(line)
        return duplicated_blocks

    def prompt(self, analysis, code):
        if not analysis:
            return code

        return f"""
You are a Python refactoring agent.

Extract duplicated logic into reusable functions.
Return ONLY the refactored Python code.

CODE:
{code}
"""
