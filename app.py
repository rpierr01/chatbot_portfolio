import streamlit as st
import sys
import os
from datetime import datetime
from agent import get_agent_response, load_conversation, save_conversation
import uuid

# streamlit run app.py

# Ajouter le chemin du dossier projet-iut-potfolio pour importer agent.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'projet-iut-potfolio'))

# Configuration de la page
st.set_page_config(
    page_title="Chat avec Rémi - Jumeau Virtuel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du style Synthwave
with open(os.path.join(os.path.dirname(__file__), 'assets', 'synthwave.css'), "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header technologique natif Streamlit
st.title("🤖 RÉMI AI - JUMEAU VIRTUEL")
st.subheader("⚡ Intelligence Artificielle | Science des Données | Portfolio Interactif")

# Générer ou récupérer un identifiant de session unique
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialisation de l'historique dans le session_state
if "messages" not in st.session_state:
    # Charger l'historique depuis Redis si disponible
    history = load_conversation(st.session_state.session_id)
    st.session_state.messages = history.copy() if history else []
    st.session_state.conversation_history = history.copy() if history else []
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
    avatar = "assets/icon.jpg" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input utilisateur
if prompt := st.chat_input("💬 Posez votre question à Rémi..."):
    # Ajouter le message de l'utilisateur à l'interface
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtenir la réponse de l'agent (avec session_id pour sauvegarde)
    with st.chat_message("assistant", avatar="assets/icon.jpg"):
        with st.spinner("🔮 Analyse en cours..."):
            response = get_agent_response(prompt, st.session_state.conversation_history, session_id=st.session_state.session_id)
        st.markdown(response)
    
    # Ajouter la réponse à l'interface
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Mettre à jour l'historique pour l'agent
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "assistant", "content": response})

    # Sauvegarder la conversation après chaque interaction
    save_conversation(st.session_state.session_id, st.session_state.conversation_history)

# Sidebar avec informations
with st.sidebar:
    st.header("🎯 SYSTÈME D'INFORMATION")
    
    # Métriques en temps réel avec st.metric
    st.metric(label="MESSAGES ÉCHANGÉS", value=len(st.session_state.messages))
    st.metric(label="INTERACTIONS", value=len(st.session_state.conversation_history) // 2)
    
    # Durée de session
    if "start_time" in st.session_state:
        duration = datetime.now() - st.session_state.start_time
        minutes = int(duration.total_seconds() // 60)
        st.metric(label="MINUTES DE SESSION", value=minutes)
    
    st.divider()
    
    st.header("⚙️ CAPACITÉS DU SYSTÈME")
    st.write(
        "- 🔍 Recherche Sémantique\n"
        "- 💾 Mémoire Conversationnelle\n"
        "- 🧠 IA Générative GPT-4.1\n"
        "- 📊 Analyse de Portfolio\n"
        "- ⚡ Réponses en Temps Réel"
    )
    
    st.divider()
    
    st.header("🔗 LIENS EXTERNES")
    st.link_button("🌐 VOIR MON PORTFOLIO", "https://remi-pierron.github.io/portfolio", use_container_width=True)
    
    st.divider()
    
    st.header("📡 STATUT SYSTÈME")
    st.success("🟢 OPÉRATIONNEL")
    st.caption("Modèle: gpt-4.1-nano | Latence: Optimale")
    
    st.divider()
    
    st.caption("🔐 Interface Sécurisée | © 2026 Rémi AI")
