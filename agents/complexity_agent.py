from agents.base_agent import BaseAgent

class ComplexityAgent(BaseAgent):
    def __init__(self, llm):
        self.llm = llm
        self.name = "ComplexityAgent"

    def analyze(self, code):
        nested_conditions = [line.strip() for line in code.splitlines() if line.strip().startswith("if")]
        return nested_conditions

    def apply(self, code):
        analysis = self.analyze(code)
        if analysis:
            proposal = self.llm.ask(
                "Refactor nested conditions in Python code for clarity",
                "\n".join(code.splitlines())
            )
        else:
            proposal = code
        return {"name": self.name, "analysis": analysis, "proposal": proposal}
