import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from upstash_vector import Index
from upstash_redis import Redis  # Ajout pour Redis

# Chargement des variables d'environnement
load_dotenv()

def search_portfolio(query: str) -> str:
    """
    Recherche des informations dans la base de données vectorielle Upstash.
    """
    try:
        # Connexion sécurisée (gère le cas où les variables sont absentes)
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        
        if not url or not token:
            return ""

        index = Index(url=url, token=token)
        
        # Recherche sémantique (RAG)
        # Augmentation du top_k pour récupérer plus de contexte pertinent
        results = index.query(data=query, top_k=5, include_metadata=True)
        
        if not results:
            return ""
        
        # Extraction du texte depuis les métadonnées
        context_segments: List[str] = [res.metadata.get("text", "") for res in results if res.metadata]
        return "\n\n".join(context_segments)
    
    except Exception as e:
        print(f"Note : Erreur lors de la connexion à Upstash ({e}). Le contexte ne sera pas chargé.")
        return ""

def run_agent(user_input: str, instructions: str, functions: List[callable], api_key: str, model_name: str, history: List[Dict]) -> str:
    """
    Exécute l'agent en prenant en compte l'historique de conversation.
    """
    # 1. Récupération du contexte (RAG)
    context = functions[0](user_input)
    
    # 2. Construction du message système
    # On intègre le contexte RAG directement dans le système pour cette interaction
    system_content = instructions
    if context:
        system_content += f"\n\nCONTEXTE DU PROFIL (utilise ces infos si pertinentes) :\n{context}"
    
    messages = [{"role": "system", "content": system_content}]
    
    # 3. Injection de l'historique complet (Mémoire)
    messages.extend(history)
    
    # 4. Ajout de la nouvelle question utilisateur
    messages.append({"role": "user", "content": user_input})
    
    # 5. Appel API
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de l'appel à l'API OpenAI : {e}"

# Connexion à Upstash Redis (pour la sauvegarde des conversations)
def get_redis():
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if not url or not token:
        return None
    return Redis(url=url, token=token)

def save_conversation(session_id: str, history: List[Dict]):
    """
    Sauvegarde l'historique de la conversation dans Redis.
    """
    redis = get_redis()
    if redis:
        import json
        redis.set(session_id, json.dumps(history))

def load_conversation(session_id: str) -> List[Dict]:
    """
    Charge l'historique de la conversation depuis Redis.
    """
    redis = get_redis()
    if redis:
        import json
        data = redis.get(session_id)
        if data:
            return json.loads(data)
    return []

def get_agent_response(user_input: str, history: List[Dict], session_id: str = None) -> str:
    """
    Initialise l'agent IA avec les paramètres spécifiques.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    # --- MISE À JOUR : Modèle spécifique demandé ---
    model_name = "gpt-4.1-nano"
    
    # Instructions optimisées pour éviter la répétition
    instructions = (
        "Tu es le jumeau virtuel de Rémi, étudiant en Science des Données. "
        "Ta mission est de répondre aux recruiteurs ou curieux à propos du parcours de Rémi. "
        "IMPORTANT : Tu dois répondre UNIQUEMENT en te basant sur le CONTEXTE fourni ci-dessus. "
        "Si l'information n'est pas dans le contexte, dis poliment que tu ne sais pas ou que ce n'est pas précisé dans le portfolio. "
        "N'invente RIEN (pas d'hallucinations). "
        "Sois concis, professionnel et chaleureux."
    )
    
    response = run_agent(user_input, instructions, [search_portfolio], api_key, model_name, history)
    # Sauvegarde de la conversation si session_id fourni
    if session_id is not None:
        # On ajoute la question et la réponse à l'historique
        updated_history = history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response}
        ]
        save_conversation(session_id, updated_history)
    return response

if __name__ == "__main__":
    # Initialisation de la mémoire (liste vide au départ)
    session_id = "cli-session"  # Identifiant de session simple pour le CLI
    conversation_history = load_conversation(session_id)
    
    print("--- Session Démarrée (Modèle: gpt-4.1-nano) ---")
    
    # Boucle infinie pour une conversation fluide (jusqu'à 'exit')
    while True:
        user_query = input("\nVotre question (ou 'exit') : ")
        
        if user_query.lower() in ["exit", "quit", "stop"]:
            print("Fin de la session.")
            break
        
        if not user_query.strip():
            continue

        # Appel de l'agent avec l'historique actuel
        response = get_agent_response(user_query, conversation_history, session_id=session_id)
        
        print(f"Rémi : {response}")