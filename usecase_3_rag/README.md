Use Case 3 — Pipeline d'extraction et d'analyse de documents (RAG)
Objectif

Automatiser l'ingestion, le découpage et l'indexation d'un document PDF afin de pouvoir effectuer une recherche de type RAG.

Le workflow permet de détecter automatiquement l'arrivée d'un nouveau fichier PDF dans un dossier local, puis de lancer le traitement du document jusqu'à son indexation dans une base vectorielle ChromaDB et l'envoi d'une notification Discord.

Architecture du pipeline
Dépôt d'un fichier PDF
        │
        ▼
Surveillance du dossier avec Watchdog
        │
        ▼
Extraction du texte avec pypdf
        │
        ▼
Chunking
500 tokens / overlap 100 tokens
        │
        ▼
Génération des embeddings
intfloat/multilingual-e5-base
        │
        ▼
Stockage dans ChromaDB
        │
        ▼
Test d'une requête RAG
        │
        ▼
Notification Discord

Étapes du workflow
Détection automatique d'un nouveau fichier PDF dans le dossier documents/
Extraction du texte du PDF avec pypdf
Découpage du texte en chunks de 500 tokens avec un overlap de 100 tokens
Génération des embeddings avec sentence-transformers
Stockage des textes, embeddings et métadonnées dans ChromaDB
Exécution d'une requête de test pour vérifier la recherche RAG
Envoi d'une notification Discord indiquant que le document est prêt
Automatisation

L'automatisation du workflow est réalisée avec la bibliothèque Python watchdog.

Le dossier documents/ est surveillé en permanence. Lorsqu'un nouveau fichier PDF est détecté, le programme déclenche automatiquement le pipeline complet d'ingestion.

Le mécanisme est basé sur la classe PDFHandler et la méthode on_created() :

class PDFHandler(FileSystemEventHandler):

    def on_created(self, event):


Lorsqu'un nouveau PDF est détecté, le pipeline est lancé automatiquement avec :

run_all(event.src_path)


Il n'est donc pas nécessaire de lancer manuellement chaque étape du traitement.

Document de test

Le document utilisé pour les tests est :

devis_techsolutions.pdf

Il s'agit d'un devis commercial fictif contenant notamment :

Le montant du projet : 8 500 € TTC
Un délai de réalisation de 30 jours
Un délai de paiement de 30 jours
Une garantie de 12 mois
Des informations sur la maintenance
Des informations sur la protection des données
Les informations de contact
La durée de validité du devis
Paramètres du chunking

Le découpage est réalisé au niveau des tokens.

Taille d'un chunk : 500 tokens
Overlap : 100 tokens
Pas entre deux chunks : 400 tokens

Pour le document de test, le texte extrait contient 664 tokens et produit 2 chunks :

Document : 664 tokens

Chunk 1 : 500 tokens
Chunk 2 : 264 tokens

Modèle d'embeddings

Le modèle utilisé est :

intfloat/multilingual-e5-base

Le modèle est chargé avec la bibliothèque sentence-transformers.

Les chunks sont transformés en vecteurs avant leur enregistrement dans ChromaDB.

Base vectorielle

Les données sont stockées dans une base vectorielle ChromaDB locale.

Le chemin utilisé par le script est :

./chroma_db


Chaque chunk est enregistré avec :

son texte ;
son embedding ;
le nom du document source ;
son index dans le document.

Lorsqu'un document déjà indexé est traité à nouveau, son ancienne version est supprimée avant l'ajout des nouveaux chunks.

Test RAG

Une requête de test est exécutée après l'indexation afin de vérifier que les informations pertinentes du document peuvent être retrouvées.

Exemple :

Question :

Quelle est la durée de garantie ?

Résultat :

Le projet bénéficie d'une garantie de 12 mois à compter de sa mise en production.

Ce test permet de vérifier que le document a bien été vectorisé et indexé dans ChromaDB.

Notification Discord

Une notification est envoyée automatiquement après l'indexation du document.

Exemple :

Document prêt pour le RAG

Document : devis_techsolutions.pdf
Chunks créés : 2
Statut : indexé dans ChromaDB


La notification utilise un webhook Discord configuré dans le fichier .env.

Variable utilisée :

DISCORD_WEBHOOK_URL=xxxxxxxxxxxxxxxx

Structure du projet
usecase_3_rag/
│
├── captures/
│   ├── extraction_chunking.png
│   ├── embeddings.png
│   ├── chroma_db.png
│   ├── notification_discord.png
│   ├── RAG.png
│   └── trigger.png
│
├── documents/
│   └── devis_techsolutions.pdf
│
├── ingestion.py
│
└── README.md


La base chroma_db/ est générée automatiquement lors de l'exécution et est exclue du dépôt Git.

Installation

Les dépendances utilisées sont :

pypdf
chromadb
sentence-transformers
requests
python-dotenv
watchdog


Installation avec :

pip install -r requirements.txt

Configuration

Créer un fichier .env à la racine du projet avec le webhook Discord :

DISCORD_WEBHOOK_URL=xxxxxxxxxxxxxxxx


Le fichier .env ne doit pas être publié dans le dépôt Git.

Exécution

Depuis le dossier usecase_3_rag :

python ingestion.py


Le programme affiche un menu permettant de lancer les différentes étapes :

1. Extraction & Chunking
2. Génération des embeddings
3. Stockage ChromaDB
4. Test RAG
5. Notification Discord
6. Exécuter tout le pipeline
7. Surveiller automatiquement les PDF
0. Quitter

Exécution automatique

Pour activer la surveillance automatique :

Choix : 7


Le programme commence alors à surveiller le dossier documents/.

Lorsqu'un nouveau PDF est déposé dans ce dossier, le pipeline est automatiquement déclenché.

Captures

Le dossier captures/ contient les preuves des différentes étapes du workflow :

extraction_chunking.png — extraction du texte et découpage en chunks
embeddings.png — génération des embeddings
chroma_db.png — stockage des données dans ChromaDB
RAG.png — test de recherche RAG
notification_discord.png — notification Discord
trigger.png — détection automatique d'un nouveau PDF et déclenchement du workflow
Livrable

Le Use Case 3 fournit :

Un script Python d'ingestion
Une extraction et un chunking automatisés des documents PDF
Une génération d'embeddings
Une base vectorielle ChromaDB locale
Une requête RAG de test
Une notification Discord
Une surveillance automatique du dossier documents/
Des captures d'écran illustrant les différentes étapes du workflow