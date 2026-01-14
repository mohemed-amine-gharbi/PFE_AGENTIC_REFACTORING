# agents/rename_agent.py
class RenameAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "RenameAgent"

    def analyze(self, code):
        # Détecte les noms de variables trop courts (a, b, c, f)
        lines = code.splitlines()
        vars_found = []
        for line in lines:
            for var in ["a", "b", "c", "f"]:
                if f"{var} " in line or f"{var}=" in line:
                    vars_found.append(var)
        return vars_found

    def prompt(self, analysis):
        if not analysis:
            return "No poorly named variables detected."
        return f"Rename these variables with more meaningful names:\n{', '.join(analysis)}"
