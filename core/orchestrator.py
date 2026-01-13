from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.rename_agent import RenameAgent
from core.ollama_llm_client import OllamaLLMClient

class Orchestrator:
    def __init__(self):
        llm = OllamaLLMClient(model_name="mistral:latest")
        self.agents = [
            ComplexityAgent(llm),
            DuplicationAgent(llm),
            ImportAgent(llm),
            LongFunctionAgent(llm),
            RenameAgent(llm)
        ]

    def run(self, code):
        report = {}
        for agent in self.agents:
            analysis = agent.analyze(code)
            llm_response = agent.llm.ask(agent.prompt, "\n".join(analysis))
            report[agent.__class__.__name__] = {
                "Analysis": analysis,
                "LLM Proposal": llm_response
            }
        return report
