class DuplicationAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = "Refactor duplicated code in Python"

    def analyze(self, code):
        # Détecte des lignes identiques
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        duplicates = [line for line in lines if lines.count(line) > 1]
        return list(set(duplicates))
