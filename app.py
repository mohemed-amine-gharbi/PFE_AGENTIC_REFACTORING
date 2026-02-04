# ==================== app.py ====================
# Version Streamlit unifiée avec toutes les fonctionnalités

import streamlit as st
import traceback
import os
import sys
import pandas as pd
import time
from datetime import datetime

# Ajouter le répertoire courant au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ---------------- Configuration de la page ----------------
st.set_page_config(
    page_title="Agentic IA Refactoring Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS personnalisé ----------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .agent-card {
        background-color: #F0F9FF;
        border-radius: 8px;
        padding: 12px;
        margin: 5px 0;
        border: 1px solid #BFDBFE;
    }
    .temperature-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
    }
    .temp-low { background-color: #3B82F6; }
    .temp-medium { background-color: #F59E0B; }
    .temp-high { background-color: #EF4444; }
    .status-success { color: #10B981; font-weight: bold; }
    .status-failed { color: #EF4444; font-weight: bold; }
    .patch-note { background-color: #0D0E29; padding: 8px; border-radius: 4px; margin: 4px 0; }
</style>
""", unsafe_allow_html=True)

# ---------------- En-tête principal ----------------
st.markdown('<h1 class="main-header">⚡ Agentic IA Refactoring Pro</h1>', unsafe_allow_html=True)
st.markdown("""
**Système intelligent de refactoring multi-agents avec validation automatique et contrôle de température.**
""")

# ---------------- Initialisation ----------------
def init_system():
    """Initialise le système"""
    try:
        from core.ollama_llm_client import OllamaLLMClient
        from core.orchestrator import Orchestrator
        
        # Initialiser le client LLM
        llm_client = OllamaLLMClient(model_name="mistral:latest")
        
        # Initialiser l'orchestrator
        orchestrator = Orchestrator(llm_client)
        
        # Récupérer les agents disponibles
        available_agents = orchestrator.get_available_agents()
        
        return llm_client, orchestrator, available_agents
        
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation : {e}")
        st.text(traceback.format_exc())
        return None, None, []

# ---------------- Sidebar : Configuration ----------------
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Section : Paramètres LLM
    st.subheader("🔧 Paramètres LLM")
    
    # Température globale
    temperature = st.slider(
        "🌡️ Température globale",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Contrôle la créativité (0.0 = déterministe, 1.0 = très créatif)"
    )
    
    # Modèle
    model_name = st.selectbox(
        "🤖 Modèle Ollama",
        ["mistral:latest", "llama2:latest", "codellama:latest", "phi:latest"],
        index=0
    )
    
    st.divider()
    
    # Section : Agents disponibles
    st.subheader("🤖 Agents disponibles")
    
    # Initialiser les températures si nécessaire
    if 'available_agents' not in st.session_state:
        st.session_state.available_agents = []
        st.session_state.agent_temperatures = {}
        st.session_state.agent_enabled = {}
    
    # Récupérer les agents disponibles
    if not st.session_state.available_agents:
        _, _, agents = init_system()
        if agents:
            st.session_state.available_agents = agents
            # Initialiser les températures par défaut
            from core.temperature_config import TemperatureConfig
            for agent in agents:
                if agent not in ["TestAgent", "PatchAgent", "MergeAgent"]:
                    optimal_temp = TemperatureConfig.get_temperature(agent)
                    st.session_state.agent_temperatures[agent] = optimal_temp
                    st.session_state.agent_enabled[agent] = True
    
    # Afficher les agents avec leurs températures
    for agent in st.session_state.get('available_agents', []):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            enabled = st.checkbox(
                f"**{agent}**",
                value=st.session_state.agent_enabled.get(agent, True),
                key=f"enable_{agent}"
            )
            st.session_state.agent_enabled[agent] = enabled
        
        with col2:
            if agent not in ["TestAgent", "PatchAgent", "MergeAgent"] and enabled:
                temp = st.slider(
                    "🌡️",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.agent_temperatures.get(agent, 0.3),
                    step=0.1,
                    key=f"temp_{agent}"
                )
                st.session_state.agent_temperatures[agent] = temp
    
    st.divider()
    
    # Section : Validation automatique
    st.subheader("✅ Validation")
    
    auto_patch = st.checkbox("🩹 Appliquer PatchAgent automatiquement", value=True)
    auto_test = st.checkbox("🧪 Exécuter TestAgent automatiquement", value=True)
    
    st.divider()
    
    # Section : Statut
    st.subheader("📊 Statut")
    
    # Bouton pour initialiser/rafraîchir
    if st.button("🔄 Initialiser/Rafraîchir le système"):
        st.session_state.initialized = False
        st.rerun()

# ---------------- Initialisation du système ----------------
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

if not st.session_state.initialized:
    with st.spinner("🔄 Initialisation du système..."):
        llm_client, orchestrator, available_agents = init_system()
        
        if orchestrator and available_agents:
            st.session_state.llm_client = llm_client
            st.session_state.orchestrator = orchestrator
            st.session_state.available_agents = available_agents
            st.session_state.initialized = True
            
            st.success("✅ Système initialisé avec succès!")
            st.rerun()
        else:
            st.error("❌ Échec de l'initialisation")

# ---------------- Interface principale ----------------
if st.session_state.get('initialized', False):
    orchestrator = st.session_state.orchestrator
    available_agents = st.session_state.available_agents
    
    # ---------------- Détection de langage ----------------
    LANGUAGE_MAP = {
        ".py": ("Python", "python"),
        ".js": ("JavaScript", "javascript"),
        ".ts": ("TypeScript", "typescript"),
        ".java": ("Java", "java"),
        ".cpp": ("C++", "cpp"),
        ".c": ("C", "c"),
        ".cs": ("C#", "csharp"),
        ".go": ("Go", "go"),
        ".rb": ("Ruby", "ruby"),
        ".rs": ("Rust", "rust"),
        ".php": ("PHP", "php"),
    }
    
    def detect_language(filename):
        ext = os.path.splitext(filename)[1].lower()
        return LANGUAGE_MAP.get(ext, ("Python", "python"))
    
    # ---------------- Upload de fichier ----------------
    uploaded_file = st.file_uploader(
        "📂 Téléchargez un fichier de code",
        type=["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rb", "rs", "php"]
    )
    
    if uploaded_file:
        # Lire le code
        code = uploaded_file.read().decode("utf-8")
        language_name, language_code = detect_language(uploaded_file.name)
        
        # Afficher le code original
        st.subheader("📄 Code original")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(code, language=language_code)
        
        with col2:
            # Métriques du code
            lines = len(code.split('\n'))
            chars = len(code)
            st.metric("Lignes", lines)
            st.metric("Caractères", chars)
        
        # ---------------- Sélection des agents ----------------
        st.subheader("🎯 Sélection des agents")
        
        selected_agents = []
        
        # Créer des colonnes pour l'affichage
        cols = st.columns(2)
        
        for idx, agent_name in enumerate(available_agents):
            with cols[idx % 2]:
                enabled = st.session_state.agent_enabled.get(agent_name, True)
                
                if enabled:
                    # Agents spéciaux (sans température)
                    if agent_name in ["TestAgent", "PatchAgent", "MergeAgent"]:
                        icon = "🩹" if agent_name == "PatchAgent" else "🧪" if agent_name == "TestAgent" else "🔄"
                        if st.checkbox(
                            f"{icon} **{agent_name}**",
                            value=True,
                            key=f"select_{agent_name}"
                        ):
                            selected_agents.append({
                                "name": agent_name,
                                "temperature": None  # Pas de température pour ces agents
                            })
                    else:
                        # Agents avec température
                        temp = st.session_state.agent_temperatures.get(agent_name, 0.3)
                        temp_color = "low" if temp < 0.3 else "medium" if temp < 0.7 else "high"
                        
                        # Utiliser un label personnalisé avec emoji pour l'indicateur de température
                        temp_emoji = "🟦" if temp < 0.3 else "🟨" if temp < 0.7 else "🟥"
                        
                        if st.checkbox(
                            f"{temp_emoji} **{agent_name}** (🌡️ {temp})",
                            value=True,
                            key=f"select_{agent_name}"
                        ):
                            selected_agents.append({
                                "name": agent_name,
                                "temperature": temp
                            })
        
        # ---------------- Bouton d'exécution ----------------
        st.subheader("🚀 Exécution")
        
        if st.button("LANCER LE REFACTORING COMPLET", type="primary", use_container_width=True):
            if not selected_agents:
                st.warning("⚠️ Veuillez sélectionner au moins un agent.")
            else:
                # Initialiser la barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Étape 1 : Agents de refactoring (sans TestAgent et PatchAgent)
                    status_text.text("🔄 Exécution des agents de refactoring...")
                    
                    refactoring_agents = [a for a in selected_agents if a["name"] not in ["TestAgent", "PatchAgent", "MergeAgent"]]
                    total_agents = len(refactoring_agents) + 2  # +2 pour merge et patch/test optionnels
                    
                    refactoring_results = []
                    for i, agent_info in enumerate(refactoring_agents):
                        agent_name = agent_info["name"]
                        agent_temp = agent_info["temperature"]
                        
                        status_text.text(f"⚡ {agent_name}...")
                        
                        # Exécuter l'agent
                        agent = orchestrator.agent_instances.get(agent_name)
                        if agent:
                            result = agent.apply(code, language_name, temperature=agent_temp)
                            refactoring_results.append(result)
                        
                        # Mettre à jour la progression
                        progress = int((i + 1) / total_agents * 40)
                        progress_bar.progress(progress)
                    
                    # Étape 2 : Merge
                    status_text.text("🔄 Fusion des résultats...")
                    if refactoring_results:
                        merged_code = orchestrator.merge_results(code, refactoring_results)
                    else:
                        merged_code = code
                    
                    progress_bar.progress(60)
                    
                    # Étape 3 : Patch et Test (optionnels)
                    patch_result = None
                    test_result = None
                    
                    if auto_patch and "PatchAgent" in [a["name"] for a in selected_agents]:
                        status_text.text("🩹 Application du PatchAgent...")
                        patch_agent = orchestrator.agent_instances.get("PatchAgent")
                        if patch_agent:
                            patch_result = patch_agent.apply(merged_code, language_name)
                            merged_code = patch_result["proposal"]
                    
                    progress_bar.progress(80)
                    
                    if auto_test and "TestAgent" in [a["name"] for a in selected_agents]:
                        status_text.text("🧪 Exécution des tests...")
                        test_agent = orchestrator.agent_instances.get("TestAgent")
                        if test_agent:
                            test_result = test_agent.apply(merged_code, language_name)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success("✅ Refactoring terminé avec succès!")
                    
                    # ---------------- Rapport complet ----------------
                    
                    # Section 1: Résumé des températures utilisées
                    st.subheader("📊 Rapport de températures")
                    
                    if refactoring_results:
                        temp_data = []
                        for result in refactoring_results:
                            agent_name = result.get("name", "Inconnu")
                            temp_used = result.get("temperature_used", "N/A")
                            analysis_len = len(result.get("analysis", []))
                            
                            temp_data.append({
                                "Agent": agent_name,
                                "🌡️ Température": temp_used,
                                "🔍 Problèmes détectés": analysis_len,
                                "📝 Statut": "✅" if analysis_len > 0 else "⚪"
                            })
                        
                        if temp_data:
                            df = pd.DataFrame(temp_data)
                            st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Section 2: Détails par agent
                    st.subheader("📈 Résultats détaillés")
                    
                    for result in refactoring_results:
                        agent_name = result.get("name", "Inconnu")
                        analysis = result.get("analysis", [])
                        proposal = result.get("proposal", "")
                        temp_used = result.get("temperature_used", "N/A")
                        
                        with st.expander(f"{agent_name} (🌡️ {temp_used})", expanded=False):
                            tab1, tab2 = st.tabs(["📋 Analyse", "💡 Proposition"])
                            
                            with tab1:
                                if analysis:
                                    for i, issue in enumerate(analysis, 1):
                                        st.code(issue)
                                else:
                                    st.info("Aucun problème détecté")
                            
                            with tab2:
                                if proposal and proposal != code:
                                    st.code(proposal, language=language_code)
                                else:
                                    st.info("Aucune modification proposée")
                    
                    # Section 3: Résultats PatchAgent
                    if patch_result:
                        st.subheader("🩹 Résultats PatchAgent")
                        
                        analysis = patch_result.get("analysis", [])
                        if analysis:
                            for note in analysis:
                                if isinstance(note, dict):
                                    st.markdown(f"<div class='patch-note'>{note.get('note', '')}</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='patch-note'>{str(note)}</div>", unsafe_allow_html=True)
                        
                        changes = patch_result.get("changes_applied", [])
                        if changes:
                            st.markdown("**Changements appliqués:**")
                            for change in changes:
                                st.markdown(f"- {change}")
                    
                    # Section 4: Résultats TestAgent
                    if test_result:
                        st.subheader("🧪 Résultats TestAgent")
                        
                        # Statut général avec mise en forme conditionnelle
                        status = test_result.get("status", "N/A")
                        if status == "SUCCESS":
                            status_display = f"**Statut général :** ✅ **{status}**"
                        else:
                            status_display = f"**Statut général :** ❌ **{status}**"
                        st.markdown(status_display)
                        
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
                                
                                status_icon = "✅" if status_tool == "SUCCESS" else "❌"
                                with st.expander(f"{status_icon} Outil : {tool} | Status : {status_tool}"):
                                    if output:
                                        lines = output.splitlines()
                                        main_line = lines[0] if lines else ""
                                        rest_lines = "\n".join(lines[1:]) if len(lines) > 1 else ""
                                        st.markdown(f"**Message principal :** {main_line}")
                                        if rest_lines:
                                            st.code(rest_lines)
                    
                    # Section 5: Code final
                    st.subheader("📝 Code final refactoré")
                    st.code(merged_code, language=language_code)
                    
                    # Téléchargement
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "💾 TÉLÉCHARGER LE CODE",
                            data=merged_code,
                            file_name=f"refactored_{uploaded_file.name}",
                            mime=f"text/{language_code}",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Différences
                        if st.button("🔍 VOIR LES DIFFÉRENCES", use_container_width=True):
                            import difflib
                            diff = difflib.unified_diff(
                                code.splitlines(keepends=True),
                                merged_code.splitlines(keepends=True),
                                fromfile='original',
                                tofile='refactoré',
                                lineterm=''
                            )
                            diff_text = '\n'.join(diff)
                            
                            if diff_text:
                                st.subheader("Différences")
                                st.code(diff_text, language="diff")
                            else:
                                st.info("Aucune différence (code identique)")
                    
                except Exception as e:
                    st.error(f"❌ Erreur pendant l'exécution : {e}")
                    st.text(traceback.format_exc())
    
    else:
        # ---------------- Section d'accueil ----------------
        st.info("👋 **Bienvenue !** Téléchargez un fichier de code pour commencer.")
        
        # Exemple de code
        with st.expander("📝 Exemple de code avec problèmes", expanded=False):
            example_code = """# Exemple de code Python avec des problèmes typiques
import os
import sys
import math

# Variable mal nommée
x = 10
y = 20

# Fonction trop longue avec logique complexe
def calc(a, b):
    result = a + b
    if result > 10:
        if result < 20:
            if result % 2 == 0:
                return result * 2
            else:
                return result * 3
        else:
            return result
    return result

# Duplication de code
def process_items(items):
    output = []
    for item in items:
        if item > 0:
            output.append(item * 2)
    return output

def transform_data(data):
    result = []
    for d in data:
        if d > 0:
            result.append(d * 2)
    return result

# Import inutilisé
import datetime  # Jamais utilisé"""
            
            st.code(example_code, language="python")
            
            if st.button("📥 Tester avec cet exemple"):
                st.session_state.example_code = example_code
                # Créer un faux fichier uploadé
                st.rerun()
        
        # Agents disponibles
        st.subheader("🤖 Agents disponibles dans le système")
        
        for agent in available_agents:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{agent}**")
                with col2:
                    if agent not in ["TestAgent", "PatchAgent", "MergeAgent"]:
                        temp = st.session_state.agent_temperatures.get(agent, 0.3)
                        st.markdown(f"🌡️ {temp}")
                with col3:
                    enabled = st.session_state.agent_enabled.get(agent, True)
                    status = "✅ Activé" if enabled else "❌ Désactivé"
                    st.markdown(status)

else:
    # ---------------- Message d'erreur ----------------
    st.error("""
    ## ❌ Système non initialisé
    
    Le système n'a pas pu être initialisé. Vérifiez :
    
    1. **Ollama est-il installé et en cours d'exécution ?**
       ```bash
       ollama --version
       ollama pull mistral:latest
       ollama serve
       ```
    
    2. **Les dépendances sont-elles installées ?**
       ```bash
       pip install streamlit pandas
       pip install ruff  # Pour TestAgent
       ```
    
    3. **Cliquez sur '🔄 Initialiser/Rafraîchir le système' dans la sidebar.**
    """)

# ---------------- Pied de page ----------------
st.divider()
st.caption("Agentic IA Refactoring Pro v2.0 • Fusion des deux projets • Développé avec Streamlit et Ollama")