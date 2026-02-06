"""
Construction du graphe LangGraph pour le refactoring.
"""

from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END
from .workflow_state import RefactorState
from .workflow_nodes import *

def build_refactor_graph(orchestrator) -> StateGraph:
    """
    Construit le graphe de refactoring intelligent.
    
    Args:
        orchestrator: Instance de LangGraphOrchestrator avec les agents
        
    Returns:
        StateGraph: Graphe compilé prêt à l'exécution
    """
    # Créer le graphe
    graph = StateGraph(RefactorState)
    
    # Ajouter les nœuds
    graph.add_node("initialize", initialize_node)
    graph.add_node("analyze_issues", analyze_issues_node)
    graph.add_node("merge_results", merge_results_node)
    graph.add_node("apply_patch", apply_patch_node)
    graph.add_node("run_tests", run_tests_node)
    graph.add_node("finalize", finalize_node)
    graph.add_node("handle_error", handle_error_node)
    
    # Ajouter des nœuds dynamiques pour chaque agent
    # Ces nœuds seront ajoutés à la volée lors de l'exécution
    def create_agent_executor(agent_name: str):
        """Crée une fonction qui exécute un agent spécifique"""
        def execute_agent(state: RefactorState) -> RefactorState:
            return execute_refactoring_agent_node(state, agent_name)
        return execute_agent
    
    # Définir le flux principal
    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "analyze_issues")
    
    # Après l'analyse, on décide dynamiquement quel agent exécuter
    graph.add_conditional_edges(
        "analyze_issues",
        decide_next_agent_node,
        {
            "execute_refactoring_agent": "execute_refactoring_agent",
            "merge_results": "merge_results"
        }
    )
    
    # Après chaque agent, on redécide
    # Note: Les nœuds d'agents seront ajoutés dynamiquement
    
    # Suite du workflow
    graph.add_edge("merge_results", "apply_patch")
    graph.add_edge("apply_patch", "run_tests")
    graph.add_edge("run_tests", "finalize")
    graph.add_edge("finalize", END)
    
    # Gestion d'erreurs
    graph.add_edge("handle_error", END)
    
    return graph

def compile_graph(orchestrator) -> StateGraph:
    """
    Compile le graphe final avec tous les agents.
    
    Args:
        orchestrator: Instance de LangGraphOrchestrator
        
    Returns:
        StateGraph: Graphe compilé prêt à l'utilisation
    """
    graph = build_refactor_graph(orchestrator)
    
    # Ajouter un nœud pour chaque agent de refactoring
    for agent_name in orchestrator.get_refactoring_agents():
        # Créer une fonction qui exécute cet agent avec l'orchestrateur
        def create_agent_executor(name: str):
            def executor(state: RefactorState) -> RefactorState:
                # Récupérer la température configurée
                temperature = state.get("temperature_config").get_temperature(name)
                
                # Exécuter l'agent
                agent = orchestrator.agent_instances.get(name)
                if agent:
                    result = agent.apply(
                        state["current_code"],
                        state["language"],
                        temperature=temperature
                    )
                    
                    # Ajouter le résultat
                    from .workflow_state import AgentResult
                    agent_result = AgentResult(
                        name=result["name"],
                        analysis=result.get("analysis", []),
                        proposal=result.get("proposal", ""),
                        temperature_used=result.get("temperature_used")
                    )
                    
                    state["agent_results"].append(agent_result)
                    state["issues_detected"].extend(result.get("analysis", []))
                    
                    # Mettre à jour le code courant avec la proposition
                    state["current_code"] = result.get("proposal", state["current_code"])
                
                return state
            return executor
        
        # Ajouter le nœud au graphe
        graph.add_node(f"agent_{agent_name}", create_agent_executor(agent_name))
    
    return graph.compile()