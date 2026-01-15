import os
import glob
from dotenv import load_dotenv
from upstash_vector import Index

# 1. Chargement des variables d'environnement
load_dotenv()

# 2. Connexion à l'index Upstash Vector
# Les identifiants sont récupérés depuis le fichier .env
index = Index(
    url=os.getenv("UPSTASH_VECTOR_REST_URL"), 
    token=os.getenv("UPSTASH_VECTOR_REST_TOKEN")
)

def chunk_markdown(content, chunk_size=500):
    """
    Découpe le contenu Markdown en morceaux (chunks)[cite: 62].
    Ici, on utilise une logique simple par paragraphe ou par taille.
    """
    # Une approche simple consiste à diviser par sections (titres ##)
    sections = content.split("\n## ")
    chunks = []
    
    for i, section in enumerate(sections):
        if i == 0:
            chunks.append(section.strip())
        else:
            chunks.append(f"## {section.strip()}")
    return chunks

def ingest_data():
    # Chemin vers votre dossier de données
    data_path = "data/*.md"
    files = glob.glob(data_path)
    
    if not files:
        print("Aucun fichier Markdown trouvé dans le dossier 'data/'.")
        return

    print(f"Début de l'indexation de {len(files)} fichiers...")

    for file_path in files:
        file_name = os.path.basename(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Étape de découpage (Chunking) [cite: 33, 59]
        chunks = chunk_markdown(content)
        
        # Préparation des vecteurs pour Upstash
        # Note : Comme vous utilisez le modèle 'Hybrid' BAAI/bge-m3 sur Upstash, 
        # le SDK s'occupe de l'embedding si vous envoyez du texte brut.
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_name}-chunk-{i}"
            
            # Envoi vers la base de données vectorielle [cite: 95, 127]
            index.upsert(
                vectors=[
                    (
                        chunk_id, 
                        chunk,              # Le texte brut (sera transformé en vecteur par Upstash) [cite: 81]
                        {"source": file_name} # Métadonnées pour garder une trace de l'origine
                    )
                ]
            )
            print(f"Chunk indexé : {chunk_id}")

    print("Indexation terminée avec succès !")

if __name__ == "__main__":
    ingest_data()