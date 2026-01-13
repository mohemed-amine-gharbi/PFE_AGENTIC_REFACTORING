class LongFunctionAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = "Split long functions into smaller logical functions"

    def analyze(self, code):
        # Détecte fonctions trop longues (>10 lignes pour exemple)
        lines = code.splitlines()
        functions = []
        current_func = []
        inside_func = False
        for line in lines:
            if line.strip().startswith("def "):
                if current_func:
                    functions.append(current_func)
                current_func = [line]
                inside_func = True
            elif inside_func:
                current_func.append(line)
        if current_func:
            functions.append(current_func)

        long_funcs = [func for func in functions if len(func) > 10]
        return ["\n".join(func) for func in long_funcs]
