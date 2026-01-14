from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.rename_agent import RenameAgent
from core.ollama_llm_client import OllamaLLMClient

class Orchestrator:
    def __init__(self):
        # Crée le client LLM
        llm = OllamaLLMClient(model_name="mistral")

        # Initialise tous les agents avec le client LLM
        self.agents = [
            ComplexityAgent(llm),
            DuplicationAgent(llm),
            ImportAgent(llm),
            LongFunctionAgent(llm),
            RenameAgent(llm)
        ]

    def run(self, code):
        results = []
        for agent in self.agents:
            analysis = agent.analyze(code)
            prompt_text = agent.prompt(analysis)  # <-- méthode maintenant
            llm_response = agent.llm.ask(prompt_text)
            results.append((agent.name, analysis, llm_response))
        return results

