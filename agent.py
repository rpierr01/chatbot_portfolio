import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from upstash_vector import Index

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
        results = index.query(data=query, top_k=3, include_metadata=True)
        
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

def get_agent_response(user_input: str, history: List[Dict]) -> str:
    """
    Initialise l'agent IA avec les paramètres spécifiques.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    # --- MISE À JOUR : Modèle spécifique demandé ---
    model_name = "gpt-4.1-nano"
    
    # Instructions optimisées pour éviter la répétition
    instructions = (
        "Tu es le jumeau virtuel de Rémi, étudiant en Science des Données. "
        "Sois concis, professionnel et chaleureux. "
        "Réponds en utilisant le contexte fourni."
        "Ne suggère pas de demander des informations que tu ne possèdes pas."
    )
    
    return run_agent(user_input, instructions, [search_portfolio], api_key, model_name, history)

if __name__ == "__main__":
    # Initialisation de la mémoire (liste vide au départ)
    conversation_history = []
    
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
        response = get_agent_response(user_query, conversation_history)
        
        print(f"Rémi : {response}")
        
        # --- Sauvegarde dans la mémoire ---
        # On ajoute la question de l'utilisateur
        conversation_history.append({"role": "user", "content": user_query})
        # On ajoute la réponse de l'assistant
        conversation_history.append({"role": "assistant", "content": response})