# Use Case 3 — Pipeline d'extraction et d'analyse de documents

## Objectif

Automatiser l'extraction et l'indexation d'un document PDF afin de pouvoir effectuer des recherches de type RAG.

## Pipeline

1. Extraction du texte du PDF avec `pypdf`
2. Découpage du texte en chunks avec un chevauchement
3. Génération des embeddings avec `sentence-transformers`
4. Stockage des embeddings dans ChromaDB
5. Test d'une requête RAG
6. Notification Discord lorsque le document est prêt

## Document de test

Le document utilisé est `devis_techsolutions.pdf`.

Il contient notamment :

- Le montant du projet : 8 500 € TTC
- Un délai de réalisation de 30 jours
- Un délai de paiement de 30 jours
- Une garantie de 12 mois

## Paramètres du chunking

- Taille maximale : 500 tokens environ
- Overlap : 100 tokens

## Modèle d'embeddings

Le modèle utilisé est :

`all-MiniLM-L6-v2`

Chaque chunk est transformé en vecteur de dimension 384.

## Base vectorielle

Les embeddings et les textes sont stockés dans une base ChromaDB locale.

## Exécution

Depuis le dossier `usecase_3_rag` :

```bash
python ingestion.py
```

## Le script :

1. extrait le texte du PDF ;
2. découpe le texte en chunks ;
3. génère les embeddings ;
4. enregistre les données dans ChromaDB ;
5. effectue une requête de test ;
6. envoie une notification Discord lorsque le document est prêt.


## Test RAG
Une requête de test est exécutée afin de vérifier que les informations du document peuvent être retrouvées.

Exemple :

Question : `Quelle est la durée de garantie ?`

Résultat attendu : Le projet bénéficie d'une garantie de 12 mois à compter de sa mise en production.

## Notification
Une notification est envoyée automatiquement sur Discord après l'indexation du document.

Exemple :

Document prêt pour le RAG
Document : devis_techsolutions.pdf
Chunks créés : 2
Statut : indexé dans ChromaDB

## Captures

Le dossier captures/ contient les preuves des différentes étapes :

- 01_extraction_chunking.png — extraction et découpage du document
- 02_embeddings.png — génération des embeddings
- 03_chromadb.png — stockage dans ChromaDB
- 04_test_rag.png — test de recherche RAG
- 05_notification_discord.png — notification Discord