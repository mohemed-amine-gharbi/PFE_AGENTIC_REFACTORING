from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.rename_agent import RenameAgent

class Orchestrator:
    def __init__(self, llm):
        self.agents = [
            ComplexityAgent(llm),
            DuplicationAgent(llm),
            ImportAgent(llm),
            LongFunctionAgent(llm),
            RenameAgent(llm)
        ]

    def run(self, code):
        """
        Retourne un rapport complet et le code final refactoré.
        """
        results = []
        current_code = code

        for agent in self.agents:
            result = agent.apply(current_code)
            results.append(result)
            # Chaque agent peut proposer une version du code
            current_code = result.get("proposal", current_code)

        return results, current_code
