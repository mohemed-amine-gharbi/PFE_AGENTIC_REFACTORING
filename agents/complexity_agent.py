class ComplexityAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = "Refactor nested conditions in Python code"

    def analyze(self, code):
        # Détecte les conditions imbriquées
        nested = [line.strip() for line in code.splitlines() if line.strip().startswith("if")]
        return nested
