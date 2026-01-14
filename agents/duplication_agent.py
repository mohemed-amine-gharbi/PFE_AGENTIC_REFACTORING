# agents/duplication_agent.py
class DuplicationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "DuplicationAgent"

    def analyze(self, code):
        lines = code.splitlines()
        duplicates = []
        seen = set()
        for line in lines:
            if line.strip() in seen:
                duplicates.append(line.strip())
            else:
                seen.add(line.strip())
        return duplicates

    def prompt(self, analysis):
        if not analysis:
            return "No duplicated code detected."
        return f"Refactor the following duplicated lines in Python:\n{chr(10).join(analysis)}"
