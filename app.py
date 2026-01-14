# app.py - Version définitive robuste
import streamlit as st
import traceback
from core.orchestrator import Orchestrator

# --- Configuration de la page ---
st.set_page_config(page_title="Agentic IA Refactoring", layout="wide")
st.title("🛠 Agentic IA Refactoring")
st.markdown("""
Interface web pour le projet **Agentic IA Refactoring**.  
Chargez un fichier Python et laissez les agents IA analyser et proposer un refactoring dynamique.
""")

# --- Upload du fichier Python ---
uploaded_file = st.file_uploader("📂 Sélectionnez un fichier Python à refactorer", type=["py"])

if uploaded_file:
    code = uploaded_file.read().decode("utf-8")

    st.subheader("📄 Code original")
    st.code(code, language="python")

    if st.button("🚀 Lancer le refactoring"):
        st.info("Analyse en cours... Patientez...")
        try:
            # --- Initialisation de l'orchestrator ---
            orchestrator = Orchestrator()
            results, refactored_code = orchestrator.run(code)  # retourne report et code final

            st.success("✅ Refactoring terminé !")

            # --- Rapport détaillé ---
            st.subheader("📊 Rapport Agentic")
            if results and isinstance(results, list):
                for idx, item in enumerate(results):
                    agent_name = item.get("agent", f"Agent {idx+1}")
                    analysis = item.get("analysis", [])
                    changed = item.get("changed", False)
                    code_after = item.get("code", "")

                    with st.expander(agent_name):
                        st.write("**Analyse:**")
                        st.code("\n".join(analysis) if analysis else "Aucun problème détecté")
                        st.write("**Modification effectuée:**", "✅ Oui" if changed else "❌ Non")
                        st.write("**Code après agent:**")
                        st.code(code_after)

            else:
                st.info("Tous les agents ont analysé le code mais aucune modification n'a été effectuée.")

            # --- Code original et refactoré côte à côte ---
            st.subheader("📝 Comparaison Code original / Refactoré")
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

        except Exception as e:
            st.error("⚠️ Une erreur est survenue :")
            st.text(traceback.format_exc())
