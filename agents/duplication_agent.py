from agents.base_agent import BaseAgent

class DuplicationAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
        self.name = "DuplicationAgent"

    def analyze(self, code):
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        duplicates = []
        for i in range(len(lines)-2):
            block = lines[i:i+3]
            for j in range(i+1, len(lines)-2):
                if block == lines[j:j+3]:
                    duplicates.append("\n".join(block))
        return list(set(duplicates))

    def apply(self, code):
        duplicates = self.analyze(code)
        if duplicates:
            proposal = f"# Attention: blocs dupliqués détectés\n" + code
        else:
            proposal = code
        return {"name": self.name, "analysis": duplicates, "proposal": proposal}
