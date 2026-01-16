from agents.base_agent import BaseAgent

class LongFunctionAgent(BaseAgent):
    def __init__(self, llm, max_lines=10):
        self.llm = llm
        self.name = "LongFunctionAgent"
        self.max_lines = max_lines

    def analyze(self, code):
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
                if line.startswith(" ") or line.startswith("\t"):
                    current_func.append(line)
                else:
                    functions.append(current_func)
                    current_func = []
                    inside_func = False
        if current_func:
            functions.append(current_func)
        long_funcs = [f for f in functions if len(f) > self.max_lines]
        return ["\n".join(f) for f in long_funcs]

    def apply(self, code):
        long_funcs = self.analyze(code)
        if long_funcs:
            proposal = f"# Attention: fonctions longues détectées\n" + code
        else:
            proposal = code
        return {"name": self.name, "analysis": long_funcs, "proposal": proposal}
