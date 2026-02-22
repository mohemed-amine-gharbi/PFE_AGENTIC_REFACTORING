"""
Définition de l'état du workflow LangGraph.
Contient toutes les informations partagées entre les nœuds.
"""

from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentResult:
    """Résultat de l'exécution d'un agent"""
    name: str
    analysis: List[str]
    proposal: str
    temperature_used: Optional[float]
    duration: float  # ⭐ Durée en secondes
    status: str


class RefactorState(TypedDict):
    """
    État global du workflow de refactoring.
    Partagé entre tous les nœuds du graphe.
    """
    # Code et langage
    original_code: str
    language: str
    current_code: str
    
    # Agent en cours
    current_agent: Optional[str]
    
    # Résultats des agents
    agent_results: List[AgentResult]
    issues_detected: List[str]
    
    # Historique et configuration
    history: List[str]
    selected_agents: List[str]
    temperature_config: Any  # TemperatureConfig
    temperature_override: Dict[str, float]  # ⭐ Températures personnalisées
    
    # Options
    auto_patch: bool
    auto_test: bool
    
    # Métriques
    metrics: Dict[str, Any]
    
    # Résultats finaux
    error: Optional[str]
    status: str
    patch_result: Optional[Dict[str, Any]]
    test_result: Optional[Dict[str, Any]]
    final_code: Optional[str]