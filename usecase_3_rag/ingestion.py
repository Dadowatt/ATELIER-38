import os
import requests

from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

DOCUMENTS_PATH = "documents"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

CHUNK_SIZE = 500
OVERLAP = 100
MODEL_NAME = "intfloat/multilingual-e5-base"


# ============================================================
# 1. EXTRACTION ET CHUNKING
# ============================================================

def extraction_chunking(tokenizer, pdf_path):

    print("\n========================================")
    print("      1. EXTRACTION & CHUNKING")
    print("========================================")

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    if not text.strip():

        print("\nAucun texte trouvé dans le PDF.")

        return []

    # TOKENISATION DU DOCUMENT
    token_ids = tokenizer.encode(
        text,
        add_special_tokens=False,
        truncation=False
    )

    print(f"\nNombre total de tokens : "f"{len(token_ids)}")

    # CHUNKING : 500 TOKENS / OVERLAP 100
    chunks = []

    start = 0

    while start < len(token_ids):

        end = start + CHUNK_SIZE

        chunk_tokens = token_ids[start:end]

        chunk_text = tokenizer.decode(
            chunk_tokens,
            skip_special_tokens=True)

        chunks.append(chunk_text)

        start += CHUNK_SIZE - OVERLAP

    print(f"Nombre de chunks : "f"{len(chunks)}")

    # AFFICHAGE DES CHUNKS
    for i, chunk in enumerate(chunks):

        chunk_token_count = len(
            tokenizer(
                chunk,
                add_special_tokens=False,
                truncation=False,
                return_attention_mask=False
            )["input_ids"]
        )

        print(f"\n--- CHUNK {i + 1} ---")

        print(f"Nombre de tokens : "f"{chunk_token_count}")

        print(chunk[:500])

    return chunks



# ============================================================
# 2. GÉNÉRATION DES EMBEDDINGS
# ============================================================

def generate_embeddings(model, chunks):

    print("\n========================================")
    print("        2. GÉNÉRATION EMBEDDINGS")
    print("========================================")

    embeddings = model.encode(chunks)

    print(f"\nNombre d'embeddings : {len(embeddings)}")
    print(f"Taille d'un embedding : {len(embeddings[0])}")

    return embeddings



# ============================================================
# 3. STOCKAGE DANS CHROMADB
# ============================================================

def store_chromadb(chunks, embeddings, pdf_path):

    print("\n========================================")
    print("           3. STOCKAGE CHROMADB")
    print("========================================")

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # Nom du document actuellement traité
    document_name = os.path.basename(pdf_path)

    # --------------------------------------------------------
    # SUPPRESSION DE L'ANCIENNE VERSION DU DOCUMENT
    # --------------------------------------------------------

    existing = collection.get(where={
            "source": document_name
        }
    )

    existing_ids = existing["ids"]

    if existing_ids:

        collection.delete(ids=existing_ids )

        print(f"\nAncienne version de" f"{document_name} supprimée.")

    # --------------------------------------------------------
    # AJOUT DES NOUVEAUX CHUNKS
    # --------------------------------------------------------

    ids = [
        f"{document_name}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "source": document_name,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print(f"\nDocument enregistré dans ChromaDB : "
        f"{document_name}")

    print(f"Nombre total de chunks dans ChromaDB : "
        f"{collection.count()}")

    return collection


# ============================================================
# 4. TEST RAG
# ============================================================

def test_rag(model, collection):

    print("\n========================================")
    print("             4. TEST RAG")
    print("========================================")

    question = "Quelle est la durée de garantie ?"

    question_embedding = model.encode(
        [question])[0]

    results = collection.query(
        query_embeddings=[
            question_embedding.tolist()
        ], n_results=1
    )

    result = results["documents"][0][0]

    print(f"\nQuestion : {question}")
    print(f"\nRésultat :\n{result}")


# ============================================================
# 5. NOTIFICATION DISCORD
# ============================================================

def send_discord_notification(chunks, pdf_path):

    print("\n========================================")
    print("        5. NOTIFICATION DISCORD")
    print("========================================")

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:

        print("\nWebhook Discord non configuré.")

        return

    message = {
        "content": (
            "**Document prêt pour le RAG**\n\n"
            f"Document : {os.path.basename(pdf_path)}\n"
            f"Chunks créés : {len(chunks)}\n"
            "Statut : indexé dans ChromaDB"
        )
    }

    response = requests.post(webhook_url, json=message)

    if response.status_code == 204:

        print("\nNotification Discord envoyée avec succès !")

    else:

        print(f"\nErreur Discord : "
            f"{response.status_code}")


# ============================================================
# 6. PIPELINE COMPLET
# ============================================================

def run_all(pdf_path):

    print("\n========================================")
    print("          PIPELINE RAG COMPLET")
    print("========================================")

    print(f"\nDocument à traiter : "
        f"{os.path.basename(pdf_path)}")

    print("\nChargement du modèle...")

    model = SentenceTransformer(MODEL_NAME)

    tokenizer = model.tokenizer

    chunks = extraction_chunking(tokenizer, pdf_path)

    embeddings = generate_embeddings(model, chunks)

    collection = store_chromadb(chunks, embeddings, pdf_path)

    test_rag(model, collection)

    send_discord_notification(chunks, pdf_path)

    print("\n========================================")
    print("          PIPELINE TERMINÉ")
    print("========================================")



# ============================================================
# 7. SURVEILLANCE AUTOMATIQUE DU DOSSIER
# ============================================================

class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        if not event.src_path.lower().endswith(".pdf"):
            return

        print("\n========================================")
        print("        NOUVEAU PDF DÉTECTÉ")
        print("========================================")

        print( f"\nFichier détecté : "
            f"{os.path.basename(event.src_path)}")

        # Petite attente pour laisser le temps
        # au fichier de finir sa copie
        time.sleep(2)

        try:

            run_all(event.src_path)

        except Exception as e:

            print(
                f"\nErreur pendant le traitement : {e}"
            )


#fonction de surveillande
def watch_documents():

    print("\n========================================")
    print("      SURVEILLANCE AUTOMATIQUE")
    print("========================================")

    print(
        f"\nDossier surveillé : "
        f"{os.path.abspath(DOCUMENTS_PATH)}"
    )

    print("\nEn attente d'un nouveau PDF...")
    print("Appuyez sur Ctrl+C pour arrêter.\n")

    event_handler = PDFHandler()

    observer = Observer()

    observer.schedule(
        event_handler,
        DOCUMENTS_PATH,
        recursive=False
    )

    observer.start()

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        print("\n\nArrêt de la surveillance...")

        observer.stop()

    observer.join()

    print("Surveillance arrêtée.")


# ============================================================
# 7. MENU INTERACTIF
# ============================================================

def menu():

    chunks = None
    model = None
    embeddings = None
    collection = None

    pdf_path = os.path.join(
        DOCUMENTS_PATH,
        "devis_techsolutions.pdf"
    )

    while True:

        print("\n")
        print("========================================")
        print("             PIPELINE RAG")
        print("========================================")
        print()
        print("1. Extraction & Chunking")
        print("2. Génération des embeddings")
        print("3. Stockage ChromaDB")
        print("4. Test RAG")
        print("5. Notification Discord")
        print("6. Exécuter tout le pipeline")
        print("7. Surveiller automatiquement les PDF")
        print("0. Quitter")
        print()

        choix = input("Votre choix : ")

        if choix == "1":

            model = SentenceTransformer(MODEL_NAME)

            tokenizer = model.tokenizer

            chunks = extraction_chunking(tokenizer, pdf_path)

        elif choix == "2":

            if chunks is None or model is None:

                print("\nVous devez d'abord "
                    "exécuter l'étape 1.")

                continue

            embeddings = generate_embeddings(model, chunks)

        elif choix == "3":

            if chunks is None or embeddings is None:

                print("\nVous devez d'abord "
                    "exécuter les étapes 1 et 2.")

                continue

            collection = store_chromadb(
                chunks,
                embeddings,
                pdf_path
            )

        elif choix == "4":

            if model is None or collection is None:

                print("\nVous devez d'abord "
                    "exécuter les étapes précédentes.")

                continue

            test_rag(model, collection)

        elif choix == "5":

            if chunks is None:

                print("\nVous devez d'abord "
                    "exécuter l'étape 1.")

                continue

            send_discord_notification(chunks, pdf_path)

        elif choix == "6":

            run_all(pdf_path)

            chunks = None
            model = None
            embeddings = None
            collection = None

        elif choix == "7":

            watch_documents()

        elif choix == "0":

            print("\nAu revoir !")
            
            break

        else:

            print("\nChoix invalide.")


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":
    menu()
