"""
Définition du graphe LangGraph pour le workflow de refactoring.
Correction: Utilise correctement temperature_override pour chaque agent
"""

from typing import Dict, Any
import time
from langgraph.graph import StateGraph, END
from .workflow_state import RefactorState, AgentResult

MAX_PATCH_TEST_ITERATIONS = 3

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

def patch_node(state: RefactorState) -> RefactorState:
    """Nœud PatchAgent — corrige le code en tenant compte des erreurs du test."""
    print(f"\n🩹 PatchAgent (itération {state['patch_test_iteration'] + 1}/{MAX_PATCH_TEST_ITERATIONS})...")

    patch_agent = state["_orchestrator"].agent_instances.get("PatchAgent")
    if not patch_agent:
        return state

    errors = state.get("patch_test_errors", [])
    code = state["current_code"]
    language = state["language"]

    start = time.time()
    patch_result = patch_agent.apply(code, language, errors=errors)
    duration = time.time() - start

    new_state = state.copy()
    new_state["current_code"] = patch_result.get("proposal", code)
    new_state["patch_result"] = {**patch_result, "duration": duration, "status": "SUCCESS"}
    new_state["patch_test_iteration"] = state.get("patch_test_iteration", 0) + 1
    new_state["history"].append(f"PatchAgent iteration {new_state['patch_test_iteration']}")

    print(f"   ✅ Patch terminé en {duration:.2f}s")
    return new_state


def test_node(state: RefactorState) -> RefactorState:
    """Nœud TestAgent — analyse le code et collecte les erreurs."""
    print(f"\n🧪 TestAgent (itération {state['patch_test_iteration']}/{MAX_PATCH_TEST_ITERATIONS})...")

    test_agent = state["_orchestrator"].agent_instances.get("TestAgent")
    if not test_agent:
        return state

    start = time.time()
    test_result = test_agent.apply(state["current_code"], state["language"])
    duration = time.time() - start

    # Collecter les erreurs pour le prochain patch
    errors = _extract_errors(test_result)
    test_status = "passed" if not errors else "failed"

    new_state = state.copy()
    new_state["test_result"] = {**test_result, "duration": duration}
    new_state["patch_test_errors"] = errors
    new_state["patch_test_status"] = test_status
    new_state["history"].append(f"TestAgent: {test_status} ({len(errors)} erreurs)")

    icon = "✅" if test_status == "passed" else "❌"
    print(f"   {icon} Test {test_status} en {duration:.2f}s — {len(errors)} erreur(s)")
    return new_state


def route_patch_test(state: RefactorState) -> str:
    """
    Décide si on boucle (patch→test) ou si on termine.
    Conditions de sortie :
      - test passé (aucune erreur)
      - itérations max atteintes
    """
    status = state.get("patch_test_status", "pending")
    iteration = state.get("patch_test_iteration", 0)

    if status == "passed":
        print(f"\n✅ Boucle patch/test terminée — code valide après {iteration} itération(s)")
        return END

    if iteration >= MAX_PATCH_TEST_ITERATIONS:
        print(f"\n⚠️  Itérations max ({MAX_PATCH_TEST_ITERATIONS}) atteintes — sortie forcée")
        new_state = state.copy()
        new_state["patch_test_status"] = "max_reached"
        return END

    print(f"\n🔄 Erreurs détectées — nouvelle itération patch ({iteration + 1}/{MAX_PATCH_TEST_ITERATIONS})")
    return "patch"


def _extract_errors(test_result: dict) -> list:
    """Extrait toutes les erreurs ET warnings pour correction."""
    errors = []

    for detail in test_result.get("details", []):
        tool   = detail.get("tool", "")
        status = detail.get("status", "")
        output = detail.get("output", "")

        if status in ("FAILED", "WARNING") and output and not output.startswith("✅"):
            errors.append(f"[{tool}] {output[:300]}")

    return errors



def compile_graph(orchestrator) -> StateGraph:
    workflow = StateGraph(RefactorState)

    # Nœuds agents de refactoring
    for agent_name in orchestrator.get_refactoring_agents():
        workflow.add_node(agent_name, create_agent_node(orchestrator, agent_name))

    # Nœud merge
    workflow.add_node("merge", merge_node)

    # Nœuds patch/test
    workflow.add_node("patch", patch_node)
    workflow.add_node("test", test_node)

    # ---- Entrée ----
    workflow.set_conditional_entry_point(
        route_to_next_agent,
        {name: name for name in orchestrator.get_refactoring_agents()}
    )

    # ---- Transitions agents → merge ----
    for agent_name in orchestrator.get_refactoring_agents():
        workflow.add_conditional_edges(
            agent_name,
            route_to_next_agent,
            {
                **{name: name for name in orchestrator.get_refactoring_agents()},
                "merge": "merge"
            }
        )

    # ---- merge → patch ----
    workflow.add_edge("merge", "patch")

    # ---- patch → test ----
    workflow.add_edge("patch", "test")

    # ---- test → patch ou END ----
    workflow.add_conditional_edges(
        "test",
        route_patch_test,
        {"patch": "patch", END: END}
    )

    return workflow.compile()