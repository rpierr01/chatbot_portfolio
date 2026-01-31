import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from upstash_vector import Index
from upstash_redis import Redis

# On charge les variables d'environnement depuis le fichier .env
load_dotenv()

# --- Les outils que l'IA peut utiliser ---

def search_portfolio(query: str) -> str:
    """
    Cherche des infos dans la base de données vectorielle Upstash.
    C'est ce qui permet de répondre aux questions sur mon parcours, mes projets et mes compétences.
    """
    try:
        url = os.getenv("UPSTASH_VECTOR_REST_URL")
        token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
        
        if not url or not token:
            return "Erreur de configuration : Identifiants Upstash Vector manquants."

        index = Index(url=url, token=token)
        
        # On fait une recherche sémantique pour trouver les 5 meilleurs résultats
        results = index.query(data=query, top_k=5, include_metadata=True)
        
        if not results:
            return "Aucune information trouvée dans le portfolio pour cette requête."
        
        # On récupère le texte de chaque résultat trouvé
        context_segments = [res.metadata.get("text", "") for res in results if res.metadata]
        return "\n\n".join(context_segments)
    
    except Exception as e:
        print(f"Erreur Upstash Vector: {e}")
        return "Une erreur est survenue lors de la recherche dans le portfolio."

def get_current_time(timezone: str = "Europe/Paris") -> str:
    """
    Donne la date et l'heure du moment.
    Pratique quand quelqu'un me demande l'heure ou la date.
    """
    try:
        # Version simplifiée, on pourrait utiliser pytz pour gérer les fuseaux horaires correctement
        now = datetime.now()
        return now.strftime("%A %d %B %Y, %H:%M:%S")
    except Exception as e:
        return f"Erreur lors de la récupération de l'heure : {e}"

# --- Définition des outils disponibles pour l'IA ---

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

# --- Gestion de la mémoire avec Redis ---

def get_redis():
    # On recharge les variables d'environnement au cas où elles auraient changé
    load_dotenv(override=True)
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    if not url or not token:
        return None
    return Redis(url=url, token=token)

def save_conversation(session_id: str, history: List[Dict]):
    """Enregistre l'historique de conversation dans Redis avec l'heure de dernière activité."""
    try:
        redis = get_redis()
        if redis:
            # On sauvegarde d'abord le contenu de la conversation en JSON
            redis.set(session_id, json.dumps(history))
            
            # Ensuite on met à jour l'ordre chronologique des sessions
            # Le score c'est le timestamp, ça permet de trier par date
            timestamp = datetime.now().timestamp()
            redis.zadd("repo:sessions_sorted", {session_id: timestamp})
    except Exception as e:
        print(f"Erreur Redis Save: {e}")

def load_conversation(session_id: str) -> List[Dict]:
    """Récupère l'historique d'une conversation depuis Redis."""
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
    """Récupère toutes les sessions de conversation, triées de la plus récente à la plus ancienne."""
    try:
        redis = get_redis()
        if redis:
            # Migration des anciennes sessions si elles existent encore
            old_sessions = redis.smembers("repo:sessions")
            if old_sessions:
                timestamp = datetime.now().timestamp()
                pipeline = redis.pipeline()
                for s in old_sessions:
                    # On les ajoute au nouveau système pour ne pas les perdre
                    pipeline.zadd("repo:sessions_sorted", {s: timestamp})
                pipeline.delete("repo:sessions")  # On supprime l'ancien format
                pipeline.exec()

            # On récupère toutes les sessions (ordre croissant = du plus vieux au plus récent)
            sessions = redis.zrange("repo:sessions_sorted", 0, -1)
            
            # On convertit en texte et on inverse l'ordre pour avoir les plus récentes en premier
            session_list = [str(s) for s in sessions]
            return session_list[::-1]
    except Exception as e:
        print(f"Erreur Redis List: {e}")
    return []

# --- Le cerveau de l'agent IA ---

def run_agent(user_input: str, system_instructions: str, api_key: str, model_name: str, history: List[Dict]) -> str:
    """
    Fait tourner l'agent IA avec la possibilité d'utiliser des outils et de se souvenir de l'historique.
    """
    client = OpenAI(api_key=api_key)
    
    # On prépare tous les messages pour l'IA
    messages = [{"role": "system", "content": system_instructions}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})
    
    # Premier appel à l'IA (elle peut décider d'utiliser un outil)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Si l'IA veut utiliser un outil
        if response_message.tool_calls:
            # On garde en mémoire que l'IA a voulu utiliser un outil
            # C'est nécessaire pour qu'OpenAI comprenne le contexte de la suite
            messages.append(response_message)
            
            # On exécute les outils demandés par l'IA
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_TOOLS.get(function_name)
                
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # On appelle la fonction
                    # get_current_time n'a pas besoin d'arguments
                    if function_name == "get_current_time":
                         function_response = function_to_call()
                    else:
                        function_response = function_to_call(**function_args)
                    
                    # On ajoute le résultat aux messages pour que l'IA puisse l'utiliser
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    })
            
            # Deuxième appel à l'IA pour qu'elle génère sa réponse finale avec les infos récupérées
            final_response = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
            return final_response.choices[0].message.content
            
        else:
            # L'IA n'a pas eu besoin d'outil, on retourne directement sa réponse
            return response_message.content

    except Exception as e:
        return f"Erreur système IA : {str(e)}"

# --- Fonction principale utilisée par l'application ---

def get_agent_response(user_input: str, history: List[Dict], session_id: str = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = "gpt-4.1-nano"  # On peut aussi utiliser gpt-4o-mini ou gpt-3.5-turbo
    
    # Les instructions qui définissent le comportement de l'IA
    instructions = (
        "Tu es le jumeau virtuel de Rémi, étudiant en Science des Données. "
        "Tu parles TOUJOURS à la première personne ('je', 'mon'). "
        "Tu es professionnel, enthousiaste et concis. "
        "Utilise les outils à ta disposition pour chercher des informations précises dans ton portfolio si on te pose des questions sur ton parcours. "
        "Si on te demande l'heure, utilise l'outil approprié. "
        "Si l'information n'est pas trouvée, dis-le honnêtement."
        "Vouvoie toujours l'utilisateur."
    )
    
    # Pour l'instant on envoie tout l'historique à l'API
    # On pourrait filtrer les messages trop anciens si besoin
    
    response_text = run_agent(user_input, instructions, api_key, model_name, history)
    
    # Petit easter egg : après quelques messages, je propose le lien vers mon portfolio
    assistant_msgs = [m for m in history if m["role"] == "assistant"]
    if len(assistant_msgs) == 2:
        response_text += "\n\n(PS: N'hésitez pas à voir mon portfolio complet : https://remi-pierron.github.io/portfolio)"
    
    # On sauvegarde la conversation dans Redis
    if session_id:
        new_history = history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": response_text}
        ]
        save_conversation(session_id, new_history)
        
    return response_text

if __name__ == "__main__":
    # Petit mode test en ligne de commande
    print("Mode CLI - Test Agent")
    h = []
    while True:
        u = input("Vous: ")
        if u in ["exit", "q"]: break
        r = get_agent_response(u, h, "test-session")
        print(f"Rémi: {r}")
        h.append({"role": "user", "content": u})
        h.append({"role": "assistant", "content": r})