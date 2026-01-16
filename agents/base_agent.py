class BaseAgent:
    def __init__(self, llm):
        self.llm = llm

    def analyze(self, code):
        """À redéfinir dans chaque agent"""
        return []

    def prompt(self, analysis, code):
        """À redéfinir dans chaque agent"""
        return code

    def apply(self, code):
        analysis = self.analyze(code)
        proposal = self.llm.ask(self.prompt_text, self.prompt(analysis, code))
        return {
            "name": self.__class__.__name__,
            "analysis": analysis,
            "proposal": proposal
        }
