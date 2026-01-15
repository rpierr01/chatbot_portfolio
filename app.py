import streamlit as st
import sys
import os
from datetime import datetime

# streamlit run app.py

# Ajouter le chemin du dossier projet-iut-potfolio pour importer agent.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'projet-iut-potfolio'))

from agent import get_agent_response

# Configuration de la page
st.set_page_config(
    page_title="Chat avec Rémi - Jumeau Virtuel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un style technologique
st.markdown("""
<style>
    /* Background et thème général */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Header personnalisé */
    .tech-header {
        background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 210, 255, 0.3);
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .tech-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0;
    }
    
    .tech-subtitle {
        color: #e0e0e0;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Messages de chat stylisés */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 210, 255, 0.2);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Boutons modernes */
    .stButton > button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 210, 255, 0.6);
    }
    
    /* Sidebar technologique */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid rgba(0, 210, 255, 0.3);
    }
    
    /* Input de chat */
    .stChatInputContainer {
        border: 2px solid rgba(0, 210, 255, 0.3);
        border-radius: 25px;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    /* Métriques */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 210, 255, 0.1) 0%, rgba(58, 71, 213, 0.1) 100%);
        border: 1px solid rgba(0, 210, 255, 0.3);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00d2ff;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    }
    
    .metric-label {
        color: #e0e0e0;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Animation de pulsation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Texte avec effet néon */
    .neon-text {
        color: #00d2ff;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.8);
    }
    
    /* Divider technologique */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d2ff, transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header technologique
st.markdown("""
<div class="tech-header">
    <h1>🤖 RÉMI AI - JUMEAU VIRTUEL</h1>
    <p class="tech-subtitle">⚡ Intelligence Artificielle | Science des Données | Portfolio Interactif</p>
</div>
""", unsafe_allow_html=True)

# Initialisation de l'historique dans le session_state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.session_state.start_time = datetime.now()

# Layout en colonnes pour les contrôles
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("🔄 NOUVELLE CONVERSATION", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.start_time = datetime.now()
        st.rerun()

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utilisateur
if prompt := st.chat_input("💬 Posez votre question à Rémi..."):
    # Ajouter le message de l'utilisateur à l'interface
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtenir la réponse de l'agent
    with st.chat_message("assistant"):
        with st.spinner("🔮 Analyse en cours..."):
            response = get_agent_response(prompt, st.session_state.conversation_history)
        st.markdown(response)
    
    # Ajouter la réponse à l'interface
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Mettre à jour l'historique pour l'agent
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "assistant", "content": response})

# Sidebar avec informations
with st.sidebar:
    st.markdown("### 🎯 SYSTÈME D'INFORMATION")
    
    # Métriques en temps réel
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value pulse">{len(st.session_state.messages)}</div>
        <div class="metric-label">MESSAGES ÉCHANGÉS</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value neon-text">{len(st.session_state.conversation_history) // 2}</div>
        <div class="metric-label">INTERACTIONS</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Durée de session
    if "start_time" in st.session_state:
        duration = datetime.now() - st.session_state.start_time
        minutes = int(duration.total_seconds() // 60)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{minutes}</div>
            <div class="metric-label">MINUTES DE SESSION</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### ⚙️ CAPACITÉS DU SYSTÈME")
    st.markdown("""
    <div style='color: #e0e0e0; line-height: 1.8;'>
    🔍 <span class="neon-text">Recherche Sémantique</span><br>
    💾 <span class="neon-text">Mémoire Conversationnelle</span><br>
    🧠 <span class="neon-text">IA Générative GPT-4.1</span><br>
    📊 <span class="neon-text">Analyse de Portfolio</span><br>
    ⚡ <span class="neon-text">Réponses en Temps Réel</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📡 STATUT SYSTÈME")
    st.markdown("""
    <div style='color: #00d2ff;'>
    🟢 <strong>OPÉRATIONNEL</strong><br>
    <span style='color: #e0e0e0; font-size: 0.85rem;'>
    Modèle: gpt-4.1-nano<br>
    Latence: <span class="neon-text">Optimale</span>
    </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.caption("🔐 Interface Sécurisée | © 2024 Rémi AI")
