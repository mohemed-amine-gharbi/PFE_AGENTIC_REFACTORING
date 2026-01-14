class ComplexityAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "ComplexityAgent"

    def analyze(self, code):
        # Détecte les conditions imbriquées
        nested = [line.strip() for line in code.splitlines() if line.strip().startswith("if")]
        return nested

    def prompt(self, analysis):
        # Retourne un texte complet pour le LLM
        if not analysis:
            return "Aucune condition imbriquée détectée."
        return f"Refactor these nested conditions in Python code:\n{chr(10).join(analysis)}"
