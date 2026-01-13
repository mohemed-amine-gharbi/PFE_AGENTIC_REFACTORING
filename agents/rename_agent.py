class RenameAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = "Rename variables and functions for clarity"

    def analyze(self, code):
        # Détecte noms courts (1 lettre)
        words = code.replace("(", " ").replace(")", " ").replace(":", " ").split()
        short_names = [w for w in words if len(w) <= 1 and w.isidentifier()]
        return short_names
