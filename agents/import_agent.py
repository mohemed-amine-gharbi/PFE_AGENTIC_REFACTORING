# agents/import_agent.py
class ImportAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, code):
        import_lines = [
            line.strip() for line in code.splitlines()
            if line.strip().startswith("import")
        ]

        duplicates = []
        seen = set()
        for imp in import_lines:
            if imp in seen:
                duplicates.append(imp)
            else:
                seen.add(imp)

        return duplicates

    def prompt(self, analysis, code):
        if not analysis:
            return code  # 🔒 aucun changement

        return f"""
You are a Python refactoring agent.

Remove duplicated import statements.
Return ONLY the corrected Python code.

CODE:
{code}
"""
