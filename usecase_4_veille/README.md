# Use Case 4 — Agent de veille technique et génération de rapport automatisé

## 1. Présentation

Ce projet consiste à mettre en place un agent automatisé de veille technologique avec n8n.

L'objectif est de récupérer quotidiennement des actualités techniques provenant de plusieurs flux RSS, de les analyser avec un modèle de langage (LLM), de filtrer les contenus peu pertinents et les doublons, puis de sélectionner les 3 actualités les plus importantes.

Le rapport final est généré au format Markdown puis envoyé automatiquement dans un canal Discord.

---

## 2. Objectifs pédagogiques

Ce workflow permet de mettre en pratique :

- la planification automatique d'un workflow ;
- la récupération de données depuis des flux RSS ;
- la fusion et la transformation de données ;
- l'utilisation d'un LLM pour analyser et filtrer des informations ;
- la génération automatique d'un rapport Markdown ;
- l'envoi d'une notification vers Discord ;
- l'orchestration complète d'un workflow avec n8n.

---

## 3. Architecture du workflow

```text
                 Schedule Trigger
                       |
          +------------+------------+
          |                         |
          v                         v
      RSS Read                  RSS Read
       DEV.to                The Hacker News
          |                         |
          v                         v
       Limit 10                  Limit 10
          |                         |
          +------------+------------+
                       |
                       v
                     Merge
                       |
                       v
                 Code JavaScript
                       |
                       v
               Basic LLM Chain
                       ^
                       |
              OpenAI Chat Model
                       |
                       v
                 HTTP Request
                       |
                       v
                    Discord
```
---

## 4. Fonctionnement

## Étape 1 — Déclenchement
Le workflow utilise un Schedule Trigger.

Il est configuré pour exécuter automatiquement la veille une fois par jour à 08h00.

Pour les tests, le workflow peut également être exécuté manuellement depuis n8n.
---
## Étape 2 — Collecte des actualités
Deux flux RSS sont utilisés :

DEV.to : https://dev.to/feed
The Hacker News : https://feeds.feedburner.com/TheHackersNews
Chaque flux est limité à 10 articles afin de réduire la quantité de données envoyées au LLM.
---
## Étape 3 — Fusion des données
Les articles provenant des deux sources sont réunis avec un nœud Merge configuré en mode Append.

Les données sont ensuite normalisées avec un nœud Code en JavaScript afin de fournir au LLM une structure homogène.
---
## Étape 4 — Analyse par le LLM
Le Basic LLM Chain analyse les articles récupérés.

Le LLM doit :

identifier les articles pertinents ;
supprimer les doublons ;
éliminer les sujets hors sujet ;
privilégier les domaines liés à l'IA, au développement logiciel, à la cybersécurité, au cloud, à la data et à l'automatisation ;
sélectionner les 3 actualités les plus pertinentes ;
générer une synthèse courte au format Markdown.
Le rapport est volontairement limité en longueur afin de respecter la limite de taille des messages Discord.
---
## Étape 5 — Génération du rapport
Le résultat produit par le LLM contient :

le titre de l'actualité ;
la source ;
un résumé ;
l'intérêt de l'information ;
le lien vers l'article.
Le résultat est généré directement au format Markdown.
---
## Étape 6 — Diffusion
Le rapport généré est envoyé automatiquement vers Discord à l'aide d'un webhook Discord.

Le nœud HTTP Request utilise une requête HTTP POST pour transmettre le rapport au canal Discord choisi.
---
## 5. Technologies utilisées
n8n — orchestration du workflow
RSS — récupération des actualités
JavaScript — transformation des données
OpenAI / LLM — filtrage, sélection et synthèse
Discord Webhook — diffusion du rapport
Markdown — format du rapport
---
## 6. Résultat obtenu
À chaque exécution, le workflow :

récupère les actualités ;
fusionne les différentes sources ;
transmet les articles au LLM ;
sélectionne les 3 actualités les plus pertinentes ;
génère un rapport Markdown ;
envoie automatiquement le rapport sur Discord.
Exemple de résultat :
---
## Veille technologique

1. Actualité technologique
Source : DEV.to
Résumé : ...
Pourquoi : ...
Lien : ...

2. Actualité technologique
Source : The Hacker News
Résumé : ...
Pourquoi : ...
Lien : ...

3. Actualité technologique
Source : The Hacker News
Résumé : ...
Pourquoi : ...
Lien : ...

7. Tests réalisés
Un test complet de bout en bout a été réalisé.

Tous les nœuds du workflow ont été exécutés avec succès et le rapport final a été reçu dans le canal Discord.

Les captures d'écran associées à l'exécution sont disponibles dans le dossier captures/.
---

## 7. Livrables

Le dossier contient :

- l'export JSON du workflow n8n ;
- les captures d'écran illustrant la chaîne d'exécution de bout en bout ;
- le présent fichier README.

### Export du workflow

Le workflow n8n est fourni au format JSON :

`UC4-agent-veille-technologique.json`

### Captures d'écran

Les captures illustrent les différentes étapes du workflow :

- `01-workflow-complet.png` — Vue globale du workflow n8n.
- `02-schedule-trigger.png` — Configuration du déclenchement quotidien.
- `03-rss-devto.png` — Configuration et récupération du flux RSS DEV.to.
- `04-limit-devto.png` — Limitation du nombre d'articles DEV.to à 10.
- `05-rss-hackernews.png` — Configuration et récupération du flux RSS The Hacker News.
- `06-limit-hackernews.png` — Limitation du nombre d'articles The Hacker News à 10.
- `07-merge-output.png` — Fusion des deux sources RSS avec le nœud Merge et vérification du résultat.
- `08-code-javascript.png` — Transformation et normalisation des données avec JavaScript.
- `09-llm-analyse.png` — Configuration du Basic LLM Chain et du prompt d'analyse.
- `10-resultat-top3.png` — Résultat du LLM avec les 3 actualités sélectionnées au format Markdown.
- `11-http-request-discord.png` — Configuration de l'envoi du rapport vers Discord.
- `12-message-discord.png` — Réception du rapport final dans le canal Discord.

---

## 9. Conclusion
Ce workflow permet d'automatiser une veille technologique quotidienne de bout en bout.

Il illustre le principe d'orchestration avec n8n :

Déclenchement → Collecte → Transformation → Analyse IA → Synthèse → Diffusion

Le workflow peut être facilement étendu avec d'autres sources RSS, un stockage des rapports ou d'autres canaux de diffusion tels que Slack ou e-mail.

