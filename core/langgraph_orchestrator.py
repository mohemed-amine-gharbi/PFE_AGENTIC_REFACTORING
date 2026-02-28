"""
Nouvel orchestrateur basé sur LangGraph.
Version corrigée qui passe correctement temperature_override au workflow.
"""

from typing import Dict, List, Any, Optional
import time

# Import de vos agents existants
from agents.rename_agent import RenameAgent
from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.merge_agent import MergeAgent
from agents.test_agent import TestAgent
from agents.patch_agent import PatchAgent
from core.temperature_config import TemperatureConfig

# Import des nouveaux modules LangGraph
from .workflow_state import RefactorState
from .workflow_graph import compile_graph


class LangGraphOrchestrator:
    """
    Orchestrateur intelligent basé sur LangGraph.
    Version corrigée avec support complet des températures personnalisées.
    """
    
    def __init__(self, llm):
        # Instanciation de tous les agents
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
        self.temperature_config = TemperatureConfig()
        
        # Compiler le graphe LangGraph
        self.graph = compile_graph(self)
    
    def run_workflow(
        self, 
        code: str, 
        language: str, 
        selected_agents: Optional[List[str]] = None,
        auto_patch: bool = True,
        auto_test: bool = True,
        temperature_override: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Exécute le workflow complet de refactoring avec LangGraph.
        
        Args:
            code: Code source à refactorer
            language: Langage de programmation
            selected_agents: Liste des agents à exécuter (tous si None)
            auto_patch: Appliquer PatchAgent automatiquement
            auto_test: Exécuter TestAgent automatiquement
            temperature_override: Dict des températures par agent {agent_name: temperature}
            
        Returns:
            Dict avec tous les résultats incluant durées et températures
        """
        # Déterminer les agents à exécuter
        if selected_agents is None:
            selected_agents = self.get_refactoring_agents()
        
        # ⭐ Préparer temperature_override
        if temperature_override is None:
            temperature_override = {}
        
        print(f"🚀 Démarrage du workflow LangGraph avec {len(selected_agents)} agents")
        if temperature_override:
            print(f"   🌡️  Températures personnalisées: {temperature_override}")
        
        # Préparer l'état initial
        workflow_start_time = time.time()
        
        initial_state: RefactorState = {
            "_orchestrator": self,  # ⭐ référence à l'orchestrateur
            "original_code": code,
            "language": language,
            "current_code": code,
            "current_agent": None,
            "agent_results": [],
            "issues_detected": [],
            "history": [],
            "selected_agents": selected_agents,
            "temperature_config": self.temperature_config,
            "temperature_override": temperature_override,  # ⭐ IMPORTANT
            "auto_patch": auto_patch,
            "auto_test": auto_test,
            "patch_test_iteration": 0,       # ⭐ NOUVEAU
            "patch_test_errors": [],          # ⭐ NOUVEAU
            "patch_test_status": "pending",   # ⭐ NOUVEAU
            "metrics": {},
            "error": None,
            "status": "initialized",
            "patch_result": None,
            "test_result": None,
            "final_code": None
        }
        
        # Exécuter le graphe
        try:
            final_state = self.graph.invoke(initial_state)
            
            workflow_duration = time.time() - workflow_start_time
            
            # Récupérer le code après le workflow
            final_code = final_state.get("current_code", code)
            
           
            final_state["final_code"] = final_state.get("current_code", code)
            final_state["metrics"]["workflow_duration"] = workflow_duration
            
            return self._prepare_final_report(final_state)
            
        except Exception as e:
            print(f"❌ Erreur dans le workflow : {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "refactored_code": code,
                "final_code": code,
                "agent_results": []
            }
    
    def _prepare_final_report(self, final_state: RefactorState) -> Dict[str, Any]:
        """
        Prépare le rapport final à partir de l'état.
        Inclut toutes les durées et températures.
        """
        agent_results = []
        
        for agent_result in final_state.get("agent_results", []):
            agent_results.append({
                "name": agent_result.name,
                "analysis": agent_result.analysis,
                "temperature_used": agent_result.temperature_used,  # ⭐ Température
                "duration": agent_result.duration,  # ⭐ Durée
                "status": agent_result.status
            })
        
        # ⭐ Ajouter PatchAgent et TestAgent aux résultats
        patch_result = final_state.get("patch_result")
        if patch_result:
            agent_results.append({
                "name": "PatchAgent",
                "analysis": patch_result.get("analysis", []),
                "temperature_used": None,
                "duration": patch_result.get("duration", 0),
                "status": patch_result.get("status", "SUCCESS")
            })
        
        test_result = final_state.get("test_result")
        if test_result:
            agent_results.append({
                "name": "TestAgent",
                "analysis": [],
                "temperature_used": None,
                "duration": test_result.get("duration", 0),
                "status": test_result.get("status", "UNKNOWN")
            })
        
        return {
            "success": True,
            "refactored_code": final_state.get("final_code", final_state["original_code"]),
            "original_code": final_state["original_code"],
            "language": final_state["language"],
            "agent_results": agent_results,  # ⭐ Avec durées et températures
            "issues_detected": final_state.get("issues_detected", []),
            "history": final_state.get("history", []),
            "metrics": final_state.get("metrics", {}),
            "patch_result": patch_result,
            "test_result": test_result,
            "execution_time": final_state.get("metrics", {}).get("workflow_duration", 0)
        }
    
    # Méthodes compatibles avec l'ancienne API
    def run_parallel(self, code, selected_agent_names, language, temperature_override=None):
        """
        Compatibilité avec l'ancienne API.
        """
        result = self.run_workflow(
            code=code,
            language=language,
            selected_agents=selected_agent_names,
            auto_patch=False,
            auto_test=False,
            temperature_override=temperature_override
        )
        
        # Format compatible
        agent_results = []
        for agent_result in result.get("agent_results", []):
            agent_results.append({
                "name": agent_result["name"],
                "analysis": agent_result["analysis"],
                "proposal": result["refactored_code"],
                "temperature_used": agent_result.get("temperature_used"),
                "duration": agent_result.get("duration", 0)
            })
        
        return agent_results
    
    def merge_results(self, original_code, selected_results):
        """Compatibilité avec l'ancienne API."""
        if not selected_results:
            return original_code
        
        proposals = []
        for res in selected_results:
            proposal = res.get("proposal", "")
            if proposal and proposal != original_code:
                proposals.append(proposal)
        
        return self.merge_agent.merge(
            original_code, 
            proposals, 
            temperature=0.2
        )
    
    def run_patch_and_test(self, code, language, patch=True, test=True):
        """Compatibilité avec l'ancienne API."""
        patch_result = None
        test_result = None

        if patch:
            patch_agent = self.agent_instances.get("PatchAgent")
            if patch_agent:
                patch_result = patch_agent.apply(code, language=language)
                code = patch_result["proposal"]

        if test:
            test_agent = self.agent_instances.get("TestAgent")
            if test_agent:
                test_result = test_agent.apply(code, language=language)

        return code, patch_result, test_result
    
    def get_available_agents(self):
        """Retourne la liste de tous les agents disponibles"""
        return list(self.agent_instances.keys())
    
    def get_refactoring_agents(self):
        """Retourne uniquement les agents de refactoring"""
        return [name for name in self.agent_instances.keys() 
                if name not in ["TestAgent", "PatchAgent", "MergeAgent"]]


# Alias pour compatibilité
Orchestrator = LangGraphOrchestrator