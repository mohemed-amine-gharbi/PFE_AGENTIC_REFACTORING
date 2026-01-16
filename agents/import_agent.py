from agents.base_agent import BaseAgent

class ImportAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.name = "ImportAgent"

    def analyze(self, code):
        lines = code.splitlines()
        imports_seen = {}
        duplicates = []
        unused = []

        # Identifier tous les imports et doublons
        for line in lines:
            line_clean = line.strip()
            if line_clean.startswith("import ") or line_clean.startswith("from "):
                if line_clean in imports_seen:
                    duplicates.append(line_clean)
                else:
                    imports_seen[line_clean] = True

        # Identifier tous les imports inutilisés
        for imp in imports_seen:
            module_name = imp.split()[1] if len(imp.split()) > 1 else None
            # Si le nom du module n'apparaît plus ailleurs dans le code
            if module_name and module_name not in code.replace(imp, ""):
                unused.append(imp)

        return {
            "duplicates": duplicates,
            "unused": unused
        }

    def apply(self, code):
        analysis = self.analyze(code)
        lines = code.splitlines()
        to_remove = set(analysis["duplicates"] + analysis["unused"])
        new_lines = [line for line in lines if line.strip() not in to_remove]

        # Rapport clair pour tous les imports supprimés
        report = []
        if analysis["duplicates"]:
            report.append("Duplicates removed: " + ", ".join(analysis["duplicates"]))
        if analysis["unused"]:
            report.append("Unused imports removed: " + ", ".join(analysis["unused"]))
        if not report:
            report.append("No duplicates or unused imports detected.")

        return {
            "name": self.name,
            "analysis": report,
            "proposal": "\n".join(new_lines)
        }
