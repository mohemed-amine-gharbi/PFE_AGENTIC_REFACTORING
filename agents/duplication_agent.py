from agents.base_agent import BaseAgent

class DuplicationAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("DuplicationAgent", llm)

    def analyze(self, code):
        lines = code.splitlines()
        duplicates = [
            line for line in set(lines)
            if lines.count(line) > 1 and line.strip()
        ]
        return duplicates

    def build_prompt(self, analysis):
        return f"""
Detected duplicated code lines:
{analysis}

Suggest a refactoring strategy.
"""
