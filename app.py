# app.py - Version corrigée avec cache Streamlit fonctionnel

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
    page_title="Agentic IA Refactoring",
    page_icon="🛠️",
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
</style>
""", unsafe_allow_html=True)

# ---------------- En-tête principal ----------------
st.markdown('<h1 class="main-header">🛠️ Agentic IA Refactoring System</h1>', unsafe_allow_html=True)
st.markdown("""
**Système intelligent de refactoring de code utilisant une approche multi-agents avec LLM local (Ollama).**
""")

# ---------------- Initialisation simplifiée (sans cache problématique) ----------------

def init_system():
    """Initialise le système sans utiliser @st.cache_resource"""
    try:
        # Import dynamique pour éviter les problèmes de cache
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
    
    # Température
    temperature = st.slider(
        "🌡️ Température",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Contrôle la créativité (0.0 = déterministe, 1.0 = très créatif)"
    )
    
    # Modèle
    model_name = st.selectbox(
        "🤖 Modèle",
        ["mistral:latest", "llama2:latest", "codellama:latest"],
        index=0
    )
    
    st.divider()
    
    # Section : Agents
    st.subheader("🤖 Agents disponibles")
    
    # Ces valeurs seront mises à jour après l'initialisation
    if 'available_agents' not in st.session_state:
        st.session_state.available_agents = []
        st.session_state.agent_temperatures = {}
    
    # Afficher les agents disponibles
    for agent in st.session_state.get('available_agents', []):
        temp = st.slider(
            f"🌡️ {agent}",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            key=f"temp_{agent}"
        )
        st.session_state.agent_temperatures[agent] = temp
    
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
            st.session_state.agent_temperatures = {agent: 0.3 for agent in available_agents}
            
            st.success("✅ Système initialisé avec succès!")
            st.rerun()
        else:
            st.error("❌ Échec de l'initialisation")

# ---------------- Interface principale (si système initialisé) ----------------
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
    }
    
    def detect_language(filename):
        ext = os.path.splitext(filename)[1].lower()
        return LANGUAGE_MAP.get(ext, ("Python", "python"))
    
    # ---------------- Upload de fichier ----------------
    uploaded_file = st.file_uploader(
        "📂 Téléchargez un fichier de code",
        type=["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rb"]
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
        st.subheader("✅ Sélection des agents")
        
        selected_agents = []
        cols = st.columns(2)
        
        for idx, agent_name in enumerate(available_agents):
            with cols[idx % 2]:
                temp = st.session_state.agent_temperatures.get(agent_name, 0.3)
                if st.checkbox(
                    f"**{agent_name}** (🌡️ {temp})",
                    value=True,
                    key=f"select_{agent_name}"
                ):
                    selected_agents.append({
                        "name": agent_name,
                        "temperature": temp
                    })
        
        # ---------------- Bouton d'exécution ----------------
        st.subheader("🚀 Exécution")
        
        if st.button("LANCER LE REFACTORING", type="primary", use_container_width=True):
            if not selected_agents:
                st.warning("⚠️ Veuillez sélectionner au moins un agent.")
            else:
                # Initialiser la barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Exécuter les agents
                    status_text.text("🔄 Exécution des agents...")
                    
                    results = []
                    total_agents = len(selected_agents)
                    
                    for i, agent_info in enumerate(selected_agents):
                        agent_name = agent_info["name"]
                        agent_temp = agent_info["temperature"]
                        
                        status_text.text(f"⚡ {agent_name}...")
                        
                        # Exécuter l'agent
                        agent = orchestrator.agent_instances.get(agent_name)
                        if agent:
                            result = agent.apply(code, language_name, temperature=agent_temp)
                            results.append(result)
                        
                        # Mettre à jour la progression
                        progress = int((i + 1) / total_agents * 90)
                        progress_bar.progress(progress)
                    
                    # Fusionner les résultats
                    status_text.text("🔄 Fusion des résultats...")
                    final_code = orchestrator.merge_results(code, results)
                    progress_bar.progress(100)
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.success("✅ Refactoring terminé avec succès!")
                    
                    # ---------------- Affichage des résultats ----------------
                    
                    # Tableau des températures utilisées
                    st.subheader("📊 Paramètres utilisés")
                    
                    temp_data = []
                    for result in results:
                        agent_name = result.get("name", "Inconnu")
                        temp_used = result.get("temperature_used", "N/A")
                        analysis_len = len(result.get("analysis", []))
                        
                        temp_data.append({
                            "Agent": agent_name,
                            "🌡️ Température": temp_used,
                            "🔍 Problèmes": analysis_len,
                            "📝 Statut": "✅" if analysis_len > 0 else "⚪"
                        })
                    
                    if temp_data:
                        df = pd.DataFrame(temp_data)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Résultats détaillés par agent
                    st.subheader("📈 Résultats par agent")
                    
                    for result in results:
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
                    
                    # Code final
                    st.subheader("📝 Code final refactoré")
                    st.code(final_code, language=language_code)
                    
                    # Téléchargement
                    st.download_button(
                        "💾 TÉLÉCHARGER LE CODE",
                        data=final_code,
                        file_name=f"refactored_{uploaded_file.name}",
                        mime=f"text/{language_code}",
                        use_container_width=True
                    )
                    
                    # Différences
                    st.subheader("🔍 Différences")
                    
                    import difflib
                    diff = difflib.unified_diff(
                        code.splitlines(keepends=True),
                        final_code.splitlines(keepends=True),
                        fromfile='original',
                        tofile='refactoré'
                    )
                    diff_text = ''.join(diff)
                    
                    if diff_text:
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
        with st.expander("📝 Voir un exemple de code", expanded=False):
            example_code = """# Exemple de code Python avec des problèmes
import os
import sys
import math

def calc(x, y):
    result = x + y
    if result > 10:
        if result < 20:
            return result * 2
    return result

# Code dupliqué
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
    return result"""
            
            st.code(example_code, language="python")
            
            if st.button("📥 Utiliser cet exemple"):
                st.session_state.example_code = example_code
                st.rerun()
        
        # Agents disponibles
        st.subheader("🤖 Agents disponibles")
        
        for agent in available_agents:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{agent}**")
                with col2:
                    st.markdown(f"🌡️ {st.session_state.agent_temperatures.get(agent, 0.3)}")

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
    
    2. **La structure des fichiers est-elle correcte ?**
       ```
       agents/
         ├── __init__.py
         ├── base_agent.py
         ├── rename_agent.py
         └── ...
       ```
    
    3. **Cliquez sur '🔄 Initialiser/Rafraîchir le système' dans la sidebar.**
    """)

# ---------------- Pied de page ----------------
st.divider()
st.caption("Agentic IA Refactoring System v1.0 • Développé avec Streamlit et Ollama")