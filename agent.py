import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from upstash_vector import Index
from upstash_redis import Redis

# Chargement des variables d'environnement
load_dotenv()

# --- OUTILS (TOOLS) ---

def search_portfolio(query: str) -> str:
    """
    Recherche des informations dans la base de données vectorielle Upstash (RAG).
    Utilisé pour répondre aux questions sur le parcours, les projets et les compétences de Rémi.
    """
    try:
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        
        if not url or not token:
            return "Erreur de configuration : Identifiants Upstash Vector manquants."

        index = Index(url=url, token=token)
        
        # Recherche sémantique
        results = index.query(data=query, top_k=5, include_metadata=True)
        
        if not results:
            return "Aucune information trouvée dans le portfolio pour cette requête."
        
        # Extraction du texte depuis les métadonnées
        context_segments = [res.metadata.get("text", "") for res in results if res.metadata]
        return "\n\n".join(context_segments)
    
    except Exception as e:
        print(f"Erreur Upstash Vector: {e}")
        return "Une erreur est survenue lors de la recherche dans le portfolio."

def get_current_time(timezone: str = "Europe/Paris") -> str:
    """
    Retourne la date et l'heure actuelles.
    Utile si l'utilisateur demande l'heure ou la date.
    """
    try:
        # Simplification pour l'exemple, on pourrait utiliser pytz pour gérer la timezone proprement
        now = datetime.now()
        return now.strftime("%A %d %B %Y, %H:%M:%S")
    except Exception as e:
        return f"Erreur lors de la récupération de l'heure : {e}"

# --- DÉFINITION DES SCHÉMAS D'OUTILS ---

AVAILABLE_TOOLS = {
    "search_portfolio": search_portfolio,
    "get_current_time": get_current_time
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_portfolio",
            "description": "Recherche des informations sur Rémi Pierron (parcours, expérience, projets, compétences) dans son portfolio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La question ou les mots-clés pour la recherche."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Donne la date et l'heure actuelles.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    }
]

# --- GESTION REDIS (MÉMOIRE) ---

def get_redis():
    # Force reload environment variables to catch dynamic updates to .env
    load_dotenv(override=True)
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if not url or not token:
        return None
    return Redis(url=url, token=token)

def save_conversation(session_id: str, history: List[Dict]):
    """Sauvegarde l'historique dans Redis et met à jour le timestamp de session."""
    try:
        redis = get_redis()
        if redis:
            # 1. Sauvegarde du contenu (JSON)
            redis.set(session_id, json.dumps(history))
            
            # 2. Ajout/Mise à jour dans le Sorted Set pour l'ordre chronologique
            # Score = Timestamp actuel, Membre = session_id
            timestamp = datetime.now().timestamp()
            redis.zadd("repo:sessions_sorted", {session_id: timestamp})
    except Exception as e:
        print(f"Erreur Redis Save: {e}")

def load_conversation(session_id: str) -> List[Dict]:
    """Charge l'historique depuis Redis."""
    try:
        redis = get_redis()
        if redis:
            data = redis.get(session_id)
            if data:
                return json.loads(data)
    except Exception as e:
        print(f"Erreur Redis Load: {e}")
    return []

def list_sessions() -> List[str]:
    """Récupère la liste des sessions triées par date (plus récente en premier)."""
    try:
        redis = get_redis()
        if redis:
            # Migration : Si on a des anciennes sessions dans le SET "repo:sessions", on les migre
            old_sessions = redis.smembers("repo:sessions")
            if old_sessions:
                timestamp = datetime.now().timestamp()
                pipeline = redis.pipeline()
                for s in old_sessions:
                    # On les ajoute avec un timestamp actuel (ou un peu décalé) pour ne pas les perdre
                    pipeline.zadd("repo:sessions_sorted", {s: timestamp})
                pipeline.delete("repo:sessions") # On supprime l'ancien set après migration
                pipeline.exec()

            # Récupère tous les éléments du ZSET (Ordre croissant de score = Plus vieux au plus récent)
            sessions = redis.zrange("repo:sessions_sorted", 0, -1)
            
            # On convertit en string et on inverse pour avoir le plus récent en premier
            session_list = [str(s) for s in sessions]
            return session_list[::-1]
    except Exception as e:
        print(f"Erreur Redis List: {e}")
    return []

# --- MOTEUR DE L'AGENT ---

def run_agent(user_input: str, system_instructions: str, api_key: str, model_name: str, history: List[Dict]) -> str:
    """
    Exécute l'agent avec support des outils (Function Calling) et de l'historique.
    """
    client = OpenAI(api_key=api_key)
    
    # Préparation des messages
    messages = [{"role": "system", "content": system_instructions}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    
    # Premier appel au modèle (peut déclencher un outil)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Si le modèle veut utiliser un outil
        if response_message.tool_calls:
            # On ajoute la réponse intermédiaire (l'intention d'appel) à l'historique de cette exécution
            # Note: On ne l'ajoute pas forcerment à l'historique global tout de suite pour garder ça propre,
            # mais OpenAI en a besoin pour le contexte immédiat.
            messages.append(response_message)
            
            # Exécution des outils demandés
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_TOOLS.get(function_name)
                
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Appel de la fonction
                    # Note: get_current_time n'a pas d'arguments obligatoires dans notre implémentation simple
                    if function_name == "get_current_time":
                         function_response = function_to_call()
                    else:
                        function_response = function_to_call(**function_args)
                    
                    # Ajout du résultat de l'outil aux messages
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    })
            
            # Second appel au modèle pour qu'il génère la réponse finale avec les infos des outils
            final_response = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return final_response.choices[0].message.content
            
        else:
            # Pas d'outil appelé, retour direct
            return response_message.content

    except Exception as e:
        return f"Erreur système IA : {str(e)}"

# --- FONCTION PRINCIPALE APPELÉE PAR L'APP ---

def get_agent_response(user_input: str, history: List[Dict], session_id: str = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = "gpt-4.1-nano" # ou gpt-4o-mini, gpt-3.5-turbo selon disponibilité
    
    # Instructions système
    instructions = (
        "Tu es le jumeau virtuel de Rémi, étudiant en Science des Données. "
        "Tu parles TOUJOURS à la première personne ('je', 'mon'). "
        "Tu es professionnel, enthousiaste et concis. "
        "Utilise les outils à ta disposition pour chercher des informations précises dans ton portfolio si on te pose des questions sur ton parcours. "
        "Si on te demande l'heure, utilise l'outil approprié. "
        "Si l'information n'est pas trouvée, dis-le honnêtement."
    )
    
    # Nettoyage de l'historique pour l'envoi à l'API (on garde user/assistant, on évite les trucs trop vieux si besoin)
    # Pour l'instant on passe tout.
    
    response_text = run_agent(user_input, instructions, api_key, model_name, history)
    
    # Petite logique "easter egg" pour le lien portfolio (optionnel, gardé pour compatibilité)
    assistant_msgs = [m for m in history if m["role"] == "assistant"]
    if len(assistant_msgs) == 2:
        response_text += "\n\n(PS: N'hésitez pas à voir mon portfolio complet : https://remi-pierron.github.io/portfolio)"
    
    # Sauvegarde
    if session_id:
        new_history = history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response_text}
        ]
        save_conversation(session_id, new_history)
        
    return response_text

if __name__ == "__main__":
    # Test simple CLI
    print("Mode CLI - Test Agent")
    h = []
    while True:
        u = input("Vous: ")
        if u in ["exit", "q"]: break
        r = get_agent_response(u, h, "test-session")
        print(f"Rémi: {r}")
        h.append({"role": "user", "content": u})
        h.append({"role": "assistant", "content": r})