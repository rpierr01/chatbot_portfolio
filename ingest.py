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
    """
    # On commence par découper par les titres de niveau 2
    sections = content.split("\n## ")
    final_chunks = []
    
    for i, section in enumerate(sections):
        text = section.strip()
        if i > 0:
            text = f"## {text}"
            
        # Si la section est trop longue, on la redécoupe par paragraphes
        if len(text) > max_char:
            paragraphs = text.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < max_char:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        final_chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            if current_chunk:
                final_chunks.append(current_chunk.strip())
        else:
            final_chunks.append(text)
            
    return final_chunks

def ingest_data():
    # Nettoyage de l'index avant nouvelle ingestion
    print("Suppression des données précédentes...")
    index.delete("*")

    data_path = "data/*.md"
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