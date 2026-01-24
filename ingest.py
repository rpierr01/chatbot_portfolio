import os
import glob
import re
from dotenv import load_dotenv
from upstash_vector import Index

# 1. Chargement des variables d'environnement
load_dotenv()

# 2. Connexion à l'index Upstash Vector
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"), 
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

def improved_chunking(content, max_char=1000):
    """
    Découpe le contenu Markdown en sections cohérentes tout en respectant une taille maximale.
    Préserve le titre principal (H1) pour donner du contexte à chaque chunk.
    """
    # Extraction du titre principal (H1)
    h1_match = re.search(r"^#\s+(.*)", content, re.MULTILINE)
    main_title = h1_match.group(1) if h1_match else "Général"
    
    # On découpe par les titres de niveau 2
    # Le split garde le délimiteur si on utilise une capture, mais ici on split simple
    # On assume que le fichier commence par le H1, puis des H2
    
    # On sépare le préambule (avant le premier H2) du reste
    parts = re.split(r"(^##\s+.*)", content, flags=re.MULTILINE)
    
    chunks = []
    
    # Le premier élément est le préambule (H1 + intro)
    preamble = parts[0].strip()
    if preamble:
       chunks.append(preamble)
       
    # Les éléments suivants vont par paire (Titre H2, Contenu) à cause du split avec capture
    # Ou si on split sans capture, on perd le titre.
    # Avec `sections = content.split("\n## ")` c'était plus simple mais moins précis.
    
    # Reprenons la logique simple mais en renforçant le contexte
    # On ignore le H1 dans le split initial pour ne pas le casser
    
    raw_sections = content.split("\n## ")
    
    final_chunks = []
    
    for i, section in enumerate(raw_sections):
        text = section.strip()
        
        # Si c'est la première section et qu'elle contient le H1, on la garde telle quelle
        # (C'est souvent l'intro)
        if i == 0:
            full_text = text
        else:
            # Pour les sections suivantes (qui étaient des H2), on reconstruit le titre H2
            # ET on ajoute le contexte du H1 si ce n'est pas déjà inclus
            full_text = f"Contexte : {main_title}\n## {text}"
            
        # Si la section est trop longue, on la redécoupe par paragraphes
        if len(full_text) > max_char:
            paragraphs = full_text.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                # On s'assure que le contexte est rappelé si on coupe trop fin
                # (Optionnel, mais mieux pour la sécurité)
                chunk_candidate = (current_chunk + "\n\n" + para).strip()
                
                if len(chunk_candidate) < max_char:
                    current_chunk = chunk_candidate
                else:
                    if current_chunk:
                        final_chunks.append(current_chunk)
                    # Nouveau chunk : on remet le contexte si besoin
                    # Pour simplifier, on ne force pas le contexte sur CHAQUE paragraphe découpé
                    # sauf si on veut être très strict. 
                    # Ici on va simplement ajouter le paragraphe.
                    current_chunk = para
            
            if current_chunk:
                final_chunks.append(current_chunk)
        else:
            final_chunks.append(full_text)
            
    return final_chunks

def ingest_data():
    # Nettoyage de l'index avant nouvelle ingestion
    print("Suppression des données précédentes...")
    index.delete("*")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "*.md")
    files = glob.glob(data_path)
    
    if not files:
        print("Aucun fichier trouvé.")
        return

    all_vectors = [] # Liste pour le batching
    print(f"Préparation de l'indexation pour {len(files)} fichiers...")

    for file_path in files:
        file_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = improved_chunking(content)
        
        for i, chunk in enumerate(chunks):
            # Extraction du titre de la section pour les métadonnées
            title_match = re.search(r"^#+\s+(.*)", chunk)
            section_title = title_match.group(1) if title_match else "Général"
            
            chunk_id = f"{file_name}-chunk-{i}"
            
            # CRUCIAL : On ajoute 'text' dans les métadonnées car agent.py le recherche
            all_vectors.append((
                chunk_id, 
                chunk, 
                {
                    "source": file_name, 
                    "text": chunk, 
                    "section": section_title
                }
            ))

    # Envoi par lots (Batch Upsert) - Beaucoup plus efficace que l'envoi un par un
    if all_vectors:
        print(f"Envoi de {len(all_vectors)} vecteurs vers Upstash...")
        index.upsert(vectors=all_vectors)

    print("Indexation terminée avec succès !")

if __name__ == "__main__":
    ingest_data()