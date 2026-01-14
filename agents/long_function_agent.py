# agents/long_function_agent.py
class LongFunctionAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "LongFunctionAgent"

    def analyze(self, code):
        # Détecte les fonctions > 20 lignes
        lines = code.splitlines()
        results = []
        func_lines = []
        inside_func = False
        count = 0
        func_name = ""
        for line in lines:
            if line.strip().startswith("def "):
                inside_func = True
                func_lines = [line.strip()]
                func_name = line.strip().split("(")[0][4:]
                count = 1
            elif inside_func:
                func_lines.append(line.strip())
                count += 1
                if line.strip() == "":
                    inside_func = False
                    if count > 20:
                        results.append(func_name)
        return results

    def prompt(self, analysis):
        if not analysis:
            return "No long functions detected."
        return f"Refactor these long functions into smaller parts:\n{chr(10).join(analysis)}"
