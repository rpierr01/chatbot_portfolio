import streamlit as st
import sys
import os
from datetime import datetime
from agent import get_agent_response, load_conversation, save_conversation, list_sessions
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
st.title("🤖 REM-Ia / JUMEAU VIRTUEL")
st.subheader("⚡ Posez moi des questions sur mon parcours et mes projets !")

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


# --- SIDEBAR (Navigation & Infos) ---
with st.sidebar:
    st.header("🗂️ CONVERSATIONS")
    
    # 1. Bouton Nouvelle Conversation
    if st.button("➕ NOUVELLE SESSION", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.start_time = datetime.now()
        st.rerun()
    
    # 2. Sélecteur d'historique
    existing_sessions = list_sessions()
    
    # On s'assure que la session actuelle est dans la liste (cas d'une nouvelle session pas encore sauvegardée)
    # ou simplement pour que le sélecteur pointe dessus correctement.
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
        
        # Si l'utilisateur change de session via le sélecteur
        if selected_session != st.session_state.session_id:
            st.session_state.session_id = selected_session
            history = load_conversation(selected_session)
            st.session_state.messages = history.copy() if history else []
            st.session_state.conversation_history = history.copy() if history else []
            st.session_state.start_time = datetime.now() 
            st.rerun()

    st.divider()
    
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
        "- 💾 Mémoire Persistante\n"
        "- 🧠 IA Générative GPT-4.1\n"
        "- 🛠️ Outils Dynamiques\n"
        "- ⚡ Réponses en Temps Réel"
    )
    
    st.divider()
    
    st.header("🔗 LIENS EXTERNES")
    st.link_button("🌐 VOIR MON PORTFOLIO", "https://remi-pierron.github.io/portfolio", use_container_width=True)
    
    st.divider()
    
    st.header("📡 STATUT SYSTÈME")
    st.success("🟢 OPÉRATIONNEL")
    st.caption("Modèle: gpt-4.1-nano | Redis: Connecté")
    
    st.divider()
    
    st.caption("🔐 Interface Sécurisée | © 2026 Rémi AI")

# --- INTERFACE PRINCIPALE ---

# Affichage de l'historique des messages
for message in st.session_state.messages:
    if message.get("role") == "tool": continue # Masquer les retours d'outils bruts si souhaité, ou les afficher différemment
    
    # Gestion de l'avatar et du rôle
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
