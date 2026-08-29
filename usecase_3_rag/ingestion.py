import shutil
import os
import requests

from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

PDF_PATH = "documents/devis_techsolutions.pdf"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "documents"

CHUNK_SIZE = 500
OVERLAP = 100

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# 1. EXTRACTION ET CHUNKING
# ============================================================

def extraction_chunking():

    print("\n========================================")
    print("      1. EXTRACTION & CHUNKING")
    print("========================================")

    reader = PdfReader(PDF_PATH)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + CHUNK_SIZE

        chunk = words[start:end]

        chunks.append(" ".join(chunk))

        start += CHUNK_SIZE - OVERLAP

    print(f"\nDocument : {os.path.basename(PDF_PATH)}")
    print(f"Nombre de chunks : {len(chunks)}")

    for i, chunk in enumerate(chunks):

        print(f"\n--- CHUNK {i + 1} ---")
        print(chunk[:500])

    return chunks


# ============================================================
# 2. GÉNÉRATION DES EMBEDDINGS
# ============================================================

def generate_embeddings(chunks):

    print("\n========================================")
    print("        2. GÉNÉRATION EMBEDDINGS")
    print("========================================")

    print("\nChargement du modèle...")

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(chunks)

    print(f"\nNombre d'embeddings : {len(embeddings)}")
    print(f"Taille d'un embedding : {len(embeddings[0])}")

    return model, embeddings


# ============================================================
# 3. STOCKAGE DANS CHROMADB
# ============================================================

def store_chromadb(chunks, embeddings):

    print("\n========================================")
    print("           3. STOCKAGE CHROMADB")
    print("========================================")

    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    collection.add(
        ids=[
            f"chunk_{i}"
            for i in range(len(chunks))
        ],
        documents=chunks,
        embeddings=embeddings.tolist()
    )

    print("\nDocument enregistré dans ChromaDB !")
    print(f"Nombre de documents : {collection.count()}")

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
        [question]
    )[0]

    results = collection.query(
        query_embeddings=[
            question_embedding.tolist()
        ],
        n_results=1
    )

    result = results["documents"][0][0]

    print(f"\nQuestion : {question}")
    print(f"\nRésultat :\n{result}")


# ============================================================
# 5. NOTIFICATION DISCORD
# ============================================================

def send_discord_notification(chunks):

    print("\n========================================")
    print("        5. NOTIFICATION DISCORD")
    print("========================================")

    webhook_url = os.getenv(
        "DISCORD_WEBHOOK_URL"
    )

    if not webhook_url:

        print("\nWebhook Discord non configuré.")

        return

    message = {
        "content": (
            "**Document prêt pour le RAG**\n\n"
            f"Document : {os.path.basename(PDF_PATH)}\n"
            f"Chunks créés : {len(chunks)}\n"
            "Statut : indexé dans ChromaDB"
        )
    }

    response = requests.post(
        webhook_url,
        json=message
    )

    if response.status_code == 204:

        print(
            "\nNotification Discord "
            "envoyée avec succès !"
        )

    else:

        print(
            f"\nErreur Discord : "
            f"{response.status_code}"
        )


# ============================================================
# 6. PIPELINE COMPLET
# ============================================================

def run_all():

    print("\n========================================")
    print("          PIPELINE RAG COMPLET")
    print("========================================")

    chunks = extraction_chunking()

    model, embeddings = generate_embeddings(
        chunks
    )

    collection = store_chromadb(
        chunks,
        embeddings
    )

    test_rag(
        model,
        collection
    )

    send_discord_notification(
        chunks
    )

    print("\n========================================")
    print("          PIPELINE TERMINÉ")
    print("========================================")


# ============================================================
# 7. MENU INTERACTIF
# ============================================================

def menu():

    chunks = None
    model = None
    embeddings = None
    collection = None

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
        print("0. Quitter")
        print()

        choix = input("Votre choix : ")

        if choix == "1":

            chunks = extraction_chunking()

        elif choix == "2":

            if chunks is None:

                print(
                    "\nVous devez d'abord "
                    "exécuter l'étape 1."
                )

                continue

            model, embeddings = generate_embeddings(
                chunks
            )

        elif choix == "3":

            if chunks is None or embeddings is None:

                print(
                    "\nVous devez d'abord "
                    "exécuter les étapes 1 et 2."
                )

                continue

            collection = store_chromadb(
                chunks,
                embeddings
            )

        elif choix == "4":

            if model is None or collection is None:

                print(
                    "\nVous devez d'abord "
                    "exécuter les étapes précédentes."
                )

                continue

            test_rag(
                model,
                collection
            )

        elif choix == "5":

            if chunks is None:

                print(
                    "\nVous devez d'abord "
                    "exécuter l'étape 1."
                )

                continue

            send_discord_notification(
                chunks
            )

        elif choix == "6":

            run_all()

            chunks = None
            model = None
            embeddings = None
            collection = None

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
