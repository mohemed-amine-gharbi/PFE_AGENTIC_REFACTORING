"""
Définition du graphe LangGraph pour le workflow de refactoring.
Correction: Utilise correctement temperature_override pour chaque agent
"""

from typing import Dict, Any
import time
from langgraph.graph import StateGraph, END
from .workflow_state import RefactorState, AgentResult


def create_agent_node(orchestrator, agent_name: str):
    """
    Crée un nœud pour un agent spécifique.
    Utilise temperature_override si fourni.
    """
    def agent_node(state: RefactorState) -> RefactorState:
        print(f"\n🤖 Exécution de {agent_name}...")
        
        agent = orchestrator.agent_instances.get(agent_name)
        if not agent:
            print(f"⚠️  Agent {agent_name} non trouvé")
            return state
        
        current_code = state["current_code"]
        language = state["language"]
        
        # ⭐ CORRECTION: Récupérer la température depuis temperature_override
        temperature_override = state.get("temperature_override", {})
        
        if agent_name in temperature_override:
            # Température personnalisée fournie
            temperature = temperature_override[agent_name]
            print(f"   🌡️  Température personnalisée: {temperature}")
        else:
            # Température par défaut depuis config
            temperature = state["temperature_config"].get_temperature(agent_name)
            print(f"   🌡️  Température par défaut: {temperature}")
        
        # ⭐ Chronométrer l'exécution de l'agent
        start_time = time.time()
        
        try:
            # Exécuter l'agent avec la température appropriée
            result = agent.apply(current_code, language, temperature=temperature)
            
            duration = time.time() - start_time
            
            # Créer AgentResult avec toutes les infos
            agent_result = AgentResult(
                name=agent_name,
                analysis=result.get("analysis", []),
                proposal=result.get("proposal", current_code),
                temperature_used=temperature,  # ⭐ Température réellement utilisée
                duration=duration,  # ⭐ Durée réelle
                status="SUCCESS"
            )
            
            print(f"   ✅ Terminé en {duration:.2f}s")
            print(f"   📋 {len(agent_result.analysis)} problèmes détectés")
            
            # Mettre à jour l'état
            new_state = state.copy()
            new_state["agent_results"].append(agent_result)
            new_state["current_agent"] = agent_name
            new_state["current_code"] = agent_result.proposal
            new_state["issues_detected"].extend(agent_result.analysis)
            new_state["history"].append(f"{agent_name} executed")
            
            return new_state
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            
            duration = time.time() - start_time
            
            # Enregistrer l'erreur mais continuer
            agent_result = AgentResult(
                name=agent_name,
                analysis=[],
                proposal=current_code,
                temperature_used=temperature,
                duration=duration,
                status=f"FAILED: {str(e)[:100]}"
            )
            
            new_state = state.copy()
            new_state["agent_results"].append(agent_result)
            new_state["history"].append(f"{agent_name} failed: {str(e)[:50]}")
            
            return new_state
    
    return agent_node


def route_to_next_agent(state: RefactorState) -> str:
    """
    Détermine le prochain agent à exécuter.
    """
    selected_agents = state["selected_agents"]
    executed_agents = [r.name for r in state["agent_results"]]
    
    # Trouver le prochain agent non exécuté
    for agent_name in selected_agents:
        if agent_name not in executed_agents:
            return agent_name
    
    # Tous les agents ont été exécutés
    return "merge"


def merge_node(state: RefactorState) -> RefactorState:
    """
    Fusionne tous les résultats des agents.
    """
    print("\n🔄 Fusion des résultats...")
    
    # Le code actuel est déjà le résultat fusionné (chaque agent modifie current_code)
    # On garde juste le code actuel comme code final
    
    new_state = state.copy()
    new_state["status"] = "merged"
    new_state["history"].append("Results merged")
    
    print("   ✅ Fusion terminée")
    
    return new_state


def compile_graph(orchestrator) -> StateGraph:
    """
    Compile le graphe LangGraph avec tous les nœuds d'agents.
    """
    # Créer le graphe
    workflow = StateGraph(RefactorState)
    
    # Ajouter un nœud pour chaque agent de refactoring
    for agent_name in orchestrator.get_refactoring_agents():
        node_func = create_agent_node(orchestrator, agent_name)
        workflow.add_node(agent_name, node_func)
    
    # Ajouter le nœud de fusion
    workflow.add_node("merge", merge_node)
    
    # Point d'entrée : premier agent sélectionné
    workflow.set_conditional_entry_point(
        route_to_next_agent,
        {agent_name: agent_name for agent_name in orchestrator.get_refactoring_agents()}
    )
    
    # Transitions conditionnelles entre agents
    for agent_name in orchestrator.get_refactoring_agents():
        workflow.add_conditional_edges(
            agent_name,
            route_to_next_agent,
            {
                **{name: name for name in orchestrator.get_refactoring_agents()},
                "merge": "merge"
            }
        )
    
    # Après la fusion, c'est terminé
    workflow.add_edge("merge", END)
    
    return workflow.compile()