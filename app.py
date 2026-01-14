# app.py - Version définitive robuste
import streamlit as st
import traceback
from core.orchestrator import Orchestrator

# Config page
st.set_page_config(page_title="Agentic IA Refactoring", layout="wide")
st.title("🛠 Agentic IA Refactoring")
st.markdown("""
Interface web pour le projet **Agentic IA Refactoring**.  
Chargez un fichier Python et laissez les agents IA analyser et proposer un refactoring dynamique.
""")

# Upload du fichier Python
uploaded_file = st.file_uploader("📂 Sélectionnez un fichier Python à refactorer", type=["py"])

if uploaded_file:
    code = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Code original")
    st.code(code, language="python")

    if st.button("🚀 Lancer le refactoring"):
        st.info("Analyse en cours... Patientez...")
        try:
            orchestrator = Orchestrator()
            results = orchestrator.run(code)  # appel standard

            # --- Récupération sécurisée du code refactoré ---
            refactored_code = code  # fallback
            if isinstance(results, list) and len(results) > 0:
                last_item = results[-1]
                if isinstance(last_item, dict):
                    refactored_code = last_item.get("proposal", code)
                elif isinstance(last_item, (tuple, list)) and len(last_item) >= 3:
                    refactored_code = last_item[2]
                else:
                    # dernier item mais format inattendu
                    refactored_code = str(last_item)

            st.success("✅ Refactoring terminé !")

            # --- Rapport détaillé ---
            st.subheader("📊 Rapport Agentic")
            if isinstance(results, list) and len(results) > 0:
                for idx, item in enumerate(results):
                    agent_name = f"Agent {idx+1}"
                    analysis = []
                    proposal = ""

                    if isinstance(item, dict):
                        agent_name = item.get("name", agent_name)
                        analysis = item.get("analysis", [])
                        proposal = item.get("proposal", "")
                    elif isinstance(item, (tuple, list)):
                        if len(item) >= 1:
                            agent_name = str(item[0])
                        if len(item) >= 2:
                            analysis = item[1]
                        if len(item) >= 3:
                            proposal = item[2]
                    else:
                        proposal = str(item)

                    with st.expander(agent_name):
                        st.write("**Analyse:**")
                        st.code("\n".join(analysis) if isinstance(analysis, list) and analysis else "Aucun problème détecté")
                        st.write("**Proposition LLM:**")
                        st.code(proposal)
            else:
                st.info("Aucun résultat généré par les agents.")

            # --- Code original et refactoré côte à côte ---
            st.subheader("📝 Code refactoré")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Code original**")
                st.code(code, language="python")
            with col2:
                st.markdown("**Code refactoré**")
                st.code(refactored_code, language="python")
                st.download_button(
                    "💾 Télécharger le code refactoré",
                    data=refactored_code,
                    file_name="refactored_code.py",
                    mime="text/python"
                )

        except Exception as e:
            st.error("⚠️ Une erreur est survenue :")
            st.text(traceback.format_exc())
