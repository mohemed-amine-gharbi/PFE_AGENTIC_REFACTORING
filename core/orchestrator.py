from agents.rename_agent import RenameAgent
from agents.complexity_agent import ComplexityAgent
from agents.merge_agent import MergeAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent

class Orchestrator:
    def __init__(self, llm):
        # Instanciation des agents
        self.agent_instances = {
            "RenameAgent": RenameAgent(llm),
            "ComplexityAgent": ComplexityAgent(llm),
            "DuplicationAgent": DuplicationAgent(llm),
            "ImportAgent": ImportAgent(llm),
            "LongFunctionAgent": LongFunctionAgent(llm),
        }
        self.merge_agent = MergeAgent(llm)

    def run_parallel(self, code, selected_agent_names, language):
        results = []

        for name in selected_agent_names:
            agent = self.agent_instances.get(name)
            if agent:
                result = agent.apply(code, language=language)
                results.append(result)

        return results


    def merge_results(self, original_code, selected_results):
        """
        Fusionne le code original avec les propositions sélectionnées par l'utilisateur
        """
        if not selected_results:
            return original_code
        proposals = [res["proposal"] for res in selected_results]
        return self.merge_agent.merge(original_code, proposals)
