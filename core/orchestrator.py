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
            ImportAgent(llm),
            DuplicationAgent(llm),
            ComplexityAgent(llm),
            LongFunctionAgent(llm),
            RenameAgent(llm)
        ]

    def run(self, code):
        report = []
        current_code = code

        for agent in self.agents:
            analysis = agent.analyze(current_code)

            # Toujours générer un prompt
            prompt = agent.prompt(analysis, current_code)

            # Appel LLM uniquement si nécessaire
            if prompt.strip() == current_code.strip():
                refactored_code = current_code
                changed = False
            else:
                refactored_code = agent.llm.ask(prompt)
                changed = refactored_code.strip() != current_code.strip()

                if "Error" in refactored_code:
                    refactored_code = current_code
                    changed = False

            current_code = refactored_code

            report.append({
                "agent": agent.__class__.__name__,
                "analysis": analysis,
                "changed": changed,
                "code": current_code
            })

        return report, current_code
