from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.rename_agent import RenameAgent
from core.llm_client import LLMClient

class Orchestrator:
    def __init__(self):
        llm = LLMClient()
        self.agents = [
            ComplexityAgent(llm),
            DuplicationAgent(llm),
            ImportAgent(llm),
            LongFunctionAgent(llm),
            RenameAgent(llm)
        ]

    def run(self, code):
        full_report = {}
        for agent in self.agents:
            analysis = agent.analyze(code)
            llm_response = agent.reason_with_llm(analysis)
            full_report[agent.name] = {
                "analysis": analysis,
                "llm_proposal": llm_response
            }
        return full_report
