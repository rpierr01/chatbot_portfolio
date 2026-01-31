import streamlit as st
import sys
import os
from datetime import datetime
from agent import get_agent_response, load_conversation, save_conversation, list_sessions
import uuid

# streamlit run app.py

# Ajouter le chemin du dossier projet-iut-potfolio pour pouvoir importer agent.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'projet-iut-potfolio'))

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Chat avec Rémi - Jumeau Virtuel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header technologique natif Streamlit
st.title("🤖 REM-Ia / JUMEAU VIRTUEL")
st.subheader("⚡ Posez moi des questions sur mon parcours et mes projets !")

# On génère un identifiant unique pour chaque session de conversation
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# On initialise l'historique de conversation
if "messages" not in st.session_state:
    # On essaie de charger l'historique depuis Redis si il existe
    history = load_conversation(st.session_state.session_id)
    st.session_state.messages = history.copy() if history else []
    st.session_state.conversation_history = history.copy() if history else []
    st.session_state.start_time = datetime.now()


# --- BARRE LATÉRALE (Navigation & Infos) ---
with st.sidebar:
    st.header("🗂️ CONVERSATIONS")
    
    # Bouton pour démarrer une nouvelle conversation
    if st.button("➕ NOUVELLE SESSION", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.start_time = datetime.now()
        st.rerun()
    
    # Liste déroulante pour reprendre une ancienne conversation
    existing_sessions = list_sessions()
    
    # On s'assure que la session actuelle apparaît dans la liste
    # (même si c'est une nouvelle session qui n'a pas encore été sauvegardée)
    all_sessions = existing_sessions.copy()
    if st.session_state.session_id not in all_sessions:
        all_sessions.insert(0, st.session_state.session_id)
        
    if all_sessions:
        try:
            current_index = all_sessions.index(st.session_state.session_id)
        except ValueError:
            current_index = 0
            
        def format_session_label(sess_id):
            if sess_id == st.session_state.session_id and sess_id not in existing_sessions:
                return f"🆕 Nouvelle Session ({sess_id[:8]}...)"
            return f"Session {sess_id[:8]}..."

        selected_session = st.selectbox(
            "Reprendre une discussion :",
            all_sessions,
            index=current_index,
            key="session_selector",
            format_func=format_session_label
        )
        
        # Quand l'utilisateur change de session dans la liste
        if selected_session != st.session_state.session_id:
            st.session_state.session_id = selected_session
            history = load_conversation(selected_session)
            st.session_state.messages = history.copy() if history else []
            st.session_state.conversation_history = history.copy() if history else []
            st.session_state.start_time = datetime.now() 
            st.rerun()

    st.divider()
    
    st.header("🎯 SYSTÈME D'INFORMATION")
    
    # Quelques statistiques en temps réel
    st.metric(label="MESSAGES ÉCHANGÉS", value=len(st.session_state.messages))
    st.metric(label="INTERACTIONS", value=len(st.session_state.conversation_history) // 2)
    
    # Durée de la session en cours
    if "start_time" in st.session_state:
        duration = datetime.now() - st.session_state.start_time
        minutes = int(duration.total_seconds() // 60)
        st.metric(label="MINUTES DE SESSION", value=minutes)
    
    st.divider()
    
    st.header("🔗 LIENS EXTERNES")
    st.link_button("🌐 VOIR MON PORTFOLIO", "https://remi-pierron.github.io/portfolio", use_container_width=True)
    
    st.divider()
    
    st.caption("© 2026 Rémi AI")

# --- INTERFACE PRINCIPALE ---

# On affiche tous les messages de la conversation
for message in st.session_state.messages:
    if message.get("role") == "tool": continue  # On masque les appels d'outils bruts pour garder l'interface propre
    
    # On gère l'avatar et le rôle du message
    role = message["role"]
    content = message["content"]
    
    if role == "assistant":
        avatar = "assets/icon.jpg"
    elif role == "user":
        avatar = None
    else:
        avatar = None # System or Tool
        
    if role in ["user", "assistant"]:
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

# Zone de saisie pour l'utilisateur
if prompt := st.chat_input("💬 Posez votre question à Rémi..."):
    # On ajoute le message de l'utilisateur à l'interface
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # On demande à l'agent de générer une réponse
    with st.chat_message("assistant", avatar="assets/icon.jpg"):
        with st.spinner("🔮 Analyse en cours..."):
            response = get_agent_response(prompt, st.session_state.conversation_history, session_id=st.session_state.session_id)
        st.markdown(response)
    
    # On ajoute la réponse à l'interface
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # On met à jour l'historique pour que l'agent s'en souvienne
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "assistant", "content": response})

    # On sauvegarde tout ça dans Redis
    save_conversation(st.session_state.session_id, st.session_state.conversation_history)
