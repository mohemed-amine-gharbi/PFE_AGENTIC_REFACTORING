from pathlib import Path
from agents.rename_agent import RenameAgent
from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.merge_agent import MergeAgent
from agents.test_agent import TestAgent
from agents.patch_agent import PatchAgent

class Orchestrator:
    def __init__(self, llm):
        self.agent_instances = {
            "RenameAgent": RenameAgent(llm),
            "ComplexityAgent": ComplexityAgent(llm),
            "DuplicationAgent": DuplicationAgent(llm),
            "ImportAgent": ImportAgent(llm),
            "LongFunctionAgent": LongFunctionAgent(llm),
            "TestAgent": TestAgent(llm),
            "PatchAgent": PatchAgent(llm),
        }
        self.merge_agent = MergeAgent(llm)

    def run_parallel(self, code, selected_agent_names, language):
        """
        Exécute les agents de refactoring en parallèle (sans TestAgent ni PatchAgent)
        """
        results = []
        for name in selected_agent_names:
            agent = self.agent_instances.get(name)
            if agent and name not in ["TestAgent", "PatchAgent"]:
                result = agent.apply(code, language=language)
                results.append(result)
        return results

    def run_patch_and_test(self, code, language):
        """
        Applique PatchAgent et TestAgent après merge/refactoring
        """
        patch_result = None
        test_result = None

        patch_agent = self.agent_instances.get("PatchAgent")
        test_agent = self.agent_instances.get("TestAgent")

        # Appliquer le patch si disponible
        if patch_agent:
            patch_result = patch_agent.apply(code, language=language)
            code = patch_result["proposal"]

        # Exécuter les tests
        if test_agent:
            test_result = test_agent.apply(code, language=language)

        return code, patch_result, test_result

    def merge_results(self, original_code, selected_results):
        """
        Fusionne le code original avec les propositions sélectionnées par l'utilisateur
        """
        if not selected_results:
            return original_code
        proposals = [res["proposal"] for res in selected_results]
        return self.merge_agent.merge(original_code, proposals)
