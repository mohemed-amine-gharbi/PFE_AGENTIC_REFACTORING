# core/orchestrator.py - Version corrigée

from agents.rename_agent import RenameAgent
from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.merge_agent import MergeAgent
from core.temperature_config import TemperatureConfig

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
        self.temperature_config = TemperatureConfig()

    def run_parallel(self, code, selected_agent_names, language, temperature_override=None):
        results = []

        for name in selected_agent_names:
            agent = self.agent_instances.get(name)
            if agent:
                # Déterminer la température à utiliser
                if temperature_override is not None:
                    temp_to_use = temperature_override
                else:
                    # Utiliser la température optimale de l'agent
                    temp_to_use = self.temperature_config.get_temperature(name)
                
                # Appeler apply() avec le paramètre temperature
                result = agent.apply(code, language=language, temperature=temp_to_use)
                results.append(result)

        return results

    def merge_results(self, original_code, selected_results):
        """
        Fusionne le code original avec les propositions sélectionnées par l'utilisateur
        """
        if not selected_results:
            return original_code
        
        # Extraire les propositions
        proposals = []
        merge_temperature = 0.2  # Température par défaut pour la fusion
        
        for res in selected_results:
            proposal = res.get("proposal", "")
            if proposal and proposal != original_code:
                proposals.append(proposal)
        
        # Utiliser la température pour le merge
        return self.merge_agent.merge(
            original_code, 
            proposals, 
            temperature=merge_temperature
        )
    
    def get_available_agents(self):
        """Retourne la liste des agents disponibles"""
        return list(self.agent_instances.keys())