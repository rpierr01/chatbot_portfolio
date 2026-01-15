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

# Charger le CSS externe
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
