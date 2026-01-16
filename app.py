import streamlit as st
import traceback
from core.orchestrator import Orchestrator
from core.ollama_llm_client import OllamaLLMClient

# Config page
st.set_page_config(page_title="Agentic IA Refactoring", layout="wide")
st.title("🛠 Agentic IA Refactoring")
st.markdown("""
Interface web pour le projet **Agentic IA Refactoring**.  
Chargez un fichier Python et laissez les agents IA analyser et proposer un refactoring clair.
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
            llm_client = OllamaLLMClient()
            orchestrator = Orchestrator(llm_client)
            results, refactored_code = orchestrator.run(code)

            st.success("✅ Refactoring terminé !")

            # Rapport détaillé
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

            # Code original vs refactoré
            st.subheader("📝 Comparaison Code")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Code original**")
                st.code(code, language="python")
            with col2:
                st.markdown("**Code refactoré final**")
                st.code(refactored_code, language="python")
                st.download_button(
                    "💾 Télécharger le code refactoré",
                    data=refactored_code,
                    file_name="refactored_code.py",
                    mime="text/python"
                )

        except Exception:
            st.error("⚠️ Une erreur est survenue :")
            st.text(traceback.format_exc())
