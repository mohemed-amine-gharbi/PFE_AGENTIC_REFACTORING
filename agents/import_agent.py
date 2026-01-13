class ImportAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = "Remove duplicate or unused imports in Python"

    def analyze(self, code):
        imports = [line.strip() for line in code.splitlines() if line.strip().startswith("import")]
        duplicates = [imp for imp in set(imports) if imports.count(imp) > 1]
        return duplicates
