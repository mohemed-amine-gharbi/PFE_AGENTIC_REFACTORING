import streamlit as st
import traceback
import os  # <- ajouté
from core.ollama_llm_client import OllamaLLMClient
from core.orchestrator import Orchestrator

# ---------------- Page config ----------------
st.set_page_config(page_title="Agentic IA Refactoring", layout="wide")
st.title("🛠 Agentic IA Refactoring")
st.markdown("""
Interface web pour le projet **Agentic IA Refactoring**.  
Chargez un fichier et laissez les agents IA analyser et proposer un refactoring clair.
""")

# ---------------- Upload ----------------
uploaded_file = st.file_uploader("📂 Sélectionnez un fichier à refactorer", type=["py","js","ts","java","cpp","c","cs","go","rb"])

# ---------------- Détection de langage ----------------
LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rb": "Ruby",
}

def detect_language(filename):
    ext = os.path.splitext(filename)[1].lower()
    return LANGUAGE_MAP.get(ext, "Python")  # Par défaut Python

# ---------------- Créer client LLM et orchestrator ----------------
llm_client = OllamaLLMClient()
orchestrator = Orchestrator(llm_client)

# Liste des agents disponibles
available_agents = [
    "ComplexityAgent",
    "DuplicationAgent",
    "ImportAgent",
    "LongFunctionAgent",
    "RenameAgent"
]

if uploaded_file:
    code = uploaded_file.read().decode("utf-8")
    language = detect_language(uploaded_file.name)  # <- détection automatique du langage

    st.subheader("📄 Code original")
    st.code(code, language)

    st.subheader("✅ Sélection des agents")
    selected_agents = []
    for agent_name in available_agents:
        if st.checkbox(agent_name, value=True):
            selected_agents.append(agent_name)

    # ---------------- Bouton pour lancer le merge ----------------
    if st.button("🚀 Lancer le refactoring avec agents sélectionnés"):
        if not selected_agents:
            st.warning("⚠️ Veuillez sélectionner au moins un agent.")
        else:
            st.info(f"Analyse et génération en cours pour {language}... Patientez...")
            try:
                # Envoie la version originale du code à tous les agents sélectionnés
                results = orchestrator.run_parallel(code, selected_agents, language=language)  # <- ici on passe le langage détecté

                st.success("✅ Analyse terminée !")

                # Affichage des résultats par agent
                st.subheader("📊 Rapport Agentic")
                for item in results:
                    agent_name = item.get("name", "Agent inconnu")
                    analysis = item.get("analysis", [])
                    proposal = item.get("proposal", "")

                    with st.expander(agent_name):
                        st.write("**Analyse:**")
                        if isinstance(analysis, list):
                            st.code("\n".join(analysis) if analysis else "Aucun problème détecté")
                        else:
                            st.code(str(analysis))
                        st.write("**Proposition LLM / Code refactoré:**")
                        st.code(proposal)

                # ---------------- Merge final ----------------
                st.subheader("📝 Code final après merge")
                final_code = orchestrator.merge_results(code, results)
                st.code(final_code, language=language.lower())
                st.download_button(
                    "💾 Télécharger le code refactoré",
                    data=final_code,
                    file_name=f"refactored_code{os.path.splitext(uploaded_file.name)[1]}",
                    mime="text/python"
                )

            except Exception:
                st.error("⚠️ Une erreur est survenue :")
                st.text(traceback.format_exc())
