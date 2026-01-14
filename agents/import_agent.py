# agents/import_agent.py
class ImportAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "ImportAgent"

    def analyze(self, code):
        import_lines = [line.strip() for line in code.splitlines() if line.strip().startswith("import")]
        duplicates = []
        seen = set()
        for imp in import_lines:
            if imp in seen:
                duplicates.append(imp)
            else:
                seen.add(imp)
        return duplicates

    def prompt(self, analysis):
        if not analysis:
            return "No duplicate or unused imports."
        return f"Remove duplicate or unnecessary imports:\n{chr(10).join(analysis)}"
