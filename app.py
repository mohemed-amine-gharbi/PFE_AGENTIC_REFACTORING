import streamlit as st
import traceback
import os
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
uploaded_file = st.file_uploader(
    "📂 Sélectionnez un fichier à refactorer", 
    type=["py","js","ts","java","cpp","c","cs","go","rb"]
)

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
    return LANGUAGE_MAP.get(ext, "Python")

# ---------------- Créer client LLM et orchestrator ----------------
llm_client = OllamaLLMClient()
orchestrator = Orchestrator(llm_client)

available_agents = [
    "ComplexityAgent",
    "DuplicationAgent",
    "ImportAgent",
    "LongFunctionAgent",
    "RenameAgent"
]

if uploaded_file:
    code = uploaded_file.read().decode("utf-8")
    language = detect_language(uploaded_file.name)

    st.subheader("📄 Code original")
    st.code(code, language)

    st.subheader("✅ Sélection des agents")
    selected_agents = []
    for agent_name in available_agents:
        if st.checkbox(agent_name, value=True):
            selected_agents.append(agent_name)

    if st.button("🚀 Lancer le refactoring avec agents sélectionnés"):
        if not selected_agents:
            st.warning("⚠️ Veuillez sélectionner au moins un agent.")
        else:
            st.info(f"Analyse et génération en cours pour {language}... Patientez...")
            try:
                # ---------------- Étape 1 : Refactoring ----------------
                results = orchestrator.run_parallel(code, selected_agents, language=language)
                st.success("✅ Analyse des agents terminée !")

                st.subheader("📊 Rapport Agentic")
                for item in results:
                    agent_name = item.get("name", "Agent inconnu")
                    analysis = item.get("analysis", [])
                    proposal = item.get("proposal", "")

                    with st.expander(agent_name):
                        st.write("**Analyse:**")
                        if isinstance(analysis, list):
                            st.code("\n".join([str(a) for a in analysis]) if analysis else "Aucun problème détecté")
                        else:
                            st.code(str(analysis))
                        st.write("**Proposition LLM / Code refactoré:**")
                        st.code(proposal)

                # ---------------- Étape 2 : Merge ----------------
                merged_code = orchestrator.merge_results(code, results)

                # ---------------- Étape 3 : Patch + Test ----------------
                final_code, patch_result, test_result = orchestrator.run_patch_and_test(
                    merged_code, language=language
                )

                st.subheader("📝 Code final après merge et patch")
                st.code(final_code, language=language.lower())

                st.download_button(
                    "💾 Télécharger le code refactoré",
                    data=final_code,
                    file_name=f"refactored_code{os.path.splitext(uploaded_file.name)[1]}",
                    mime="text/plain"
                )

                # ---------------- Rapport PatchAgent ----------------
                if patch_result:
                    st.subheader("📝 Résultats PatchAgent")
                    for note in patch_result.get("analysis", []):
                        if isinstance(note, dict):
                            st.markdown(f"- {note.get('note', '')}")
                        else:
                            st.markdown(f"- {str(note)}")

                # ---------------- Rapport TestAgent ----------------
                if test_result:
                    st.subheader("🧪 Résultats TestAgent")

                    # Statut général avec couleur
                    status = test_result.get("status", "N/A")
                    status_color = "green" if status == "SUCCESS" else "red"
                    st.markdown(f"**Statut général :** <span style='color:{status_color}'>{status}</span>", unsafe_allow_html=True)

                    # Résumé
                    summary = test_result.get("summary", [])
                    if summary:
                        st.markdown("**Résumé :**")
                        for line in summary:
                            st.markdown(f"- {line}")

                    # Détails par outil
                    details = test_result.get("details", [])
                    if details:
                        st.markdown("**Détails par outil :**")
                        for tool_info in details:
                            tool = tool_info.get("tool", "Inconnu")
                            status_tool = tool_info.get("status", "N/A")
                            output = tool_info.get("output", "")

                            with st.expander(f"Outil : {tool} | Status : {status_tool}"):
                                if output:
                                    lines = output.splitlines()
                                    main_line = lines[0] if lines else ""
                                    rest_lines = "\n".join(lines[1:]) if len(lines) > 1 else ""
                                    st.markdown(f"**Message principal :** {main_line}")
                                    if rest_lines:
                                        st.markdown(f"**Détails :**\n```{rest_lines}```")

            except Exception:
                st.error("⚠️ Une erreur est survenue :")
                st.text(traceback.format_exc())
