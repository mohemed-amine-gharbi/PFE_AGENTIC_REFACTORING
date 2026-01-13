# orchestrator.py
from agents.import_agent import ImportAgent
from agents.rename_agent import RenameAgent
from agents.duplication_agent import DuplicationAgent
from agents.long_function_agent import LongFunctionAgent
from agents.complexity_agent import ComplexityAgent

class Orchestrator:
    def __init__(self):
        self.agents = [
            ImportAgent(),
            RenameAgent(),
            DuplicationAgent(),
            LongFunctionAgent(),
            ComplexityAgent()
        ]

    def run(self, code):
        report = {}
        for agent in self.agents:
            report[agent.name] = agent.analyze(code)
        return report
