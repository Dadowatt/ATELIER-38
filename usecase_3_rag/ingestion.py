import shutil
import os

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

# -----------------------------
# 1. Extraction du PDF
# -----------------------------

pdf_path = "documents/devis_techsolutions.pdf"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    text += page.extract_text() + "\n"


# -----------------------------
# 2. Découpage en chunks
# -----------------------------

words = text.split()

chunk_size = 500
overlap = 100

chunks = []

start = 0

while start < len(words):
    end = start + chunk_size

    chunk = words[start:end]
    chunks.append(" ".join(chunk))

    start += chunk_size - overlap


# -----------------------------
# 3. Affichage des résultats
# -----------------------------

print(f"Nombre de chunks : {len(chunks)}")

for i, chunk in enumerate(chunks):
    print(f"\n--- CHUNK {i + 1} ---")
    print(chunk[:500])


# -----------------------------
# 4. Création des embeddings
# -----------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(chunks)

print(f"\nNombre d'embeddings : {len(embeddings)}")
print(f"Taille d'un embedding : {len(embeddings[0])}")


# -----------------------------
# 5. Stockage dans ChromaDB
# -----------------------------

if os.path.exists("./chroma_db"):
    shutil.rmtree("./chroma_db")

client = chromadb.PersistentClient(path="./chroma_db")


collection = client.get_or_create_collection(
    name="documents"
)

collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings.tolist()
)

print("\nDocument enregistré dans ChromaDB !")
print(f"Nombre de documents dans ChromaDB : {collection.count()}")

# -----------------------------
# 6. Test de recherche RAG
# -----------------------------

question = "Quelle est la durée de garantie ?"

question_embedding = model.encode([question])[0]

results = collection.query(
    query_embeddings=[question_embedding.tolist()],
    n_results=1
)

print("\n--- TEST RAG ---")
print(f"Question : {question}")
print(f"Résultat : {results['documents'][0][0]}")
