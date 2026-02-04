"""
État partagé pour le workflow LangGraph de refactoring.
"""

from typing import TypedDict, List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class AgentResult:
    """Résultat d'un agent de refactoring"""
    name: str
    analysis: List[str]
    proposal: str
    temperature_used: Optional[float] = None

class RefactorState(TypedDict):
    """
    État partagé pour tout le workflow de refactoring.
    Cet objet est passé entre tous les nœuds du graphe.
    """
    # Entrée
    original_code: str
    language: str
    
    # État courant
    current_code: str
    current_agent: Optional[str]
    
    # Résultats et historique
    agent_results: List[AgentResult]
    issues_detected: List[Dict[str, Any]]
    history: List[Dict[str, Any]]
    
    # Configuration
    selected_agents: List[str]
    temperature_config: Any  # TemperatureConfig
    auto_patch: bool
    auto_test: bool
    
    # Métriques
    metrics: Dict[str, Any]
    
    # Erreurs et statut
    error: Optional[str]
    status: str  # "initialized", "analyzing", "refactoring", "patching", "testing", "completed", "failed"
    
    # Résultats finaux
    patch_result: Optional[Dict[str, Any]]
    test_result: Optional[Dict[str, Any]]
    final_code: Optional[str]