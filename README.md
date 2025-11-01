# iPhone Sentiment Analysis – Projet DIA2 (HETIC)

## 1. Présentation du projet

Ce projet vise à construire une **chaîne complète d’analyse de sentiments** sur des avis clients concernant les produits **iPhone**.  
L’objectif est de collecter, traiter, analyser et visualiser automatiquement les avis à l’aide d’une architecture **Docker–ELK (Elasticsearch + Kibana)** couplée à une **API FastAPI** et un modèle **Transformers (DistilBERT)**.

Le pipeline complet :
```
Dataset Kaggle → Nettoyage + Enrichissement → FastAPI (analyse IA)
        ↓
Elasticsearch (indexation des avis)
        ↓
Kibana (dashboard de visualisation)
```

---

## 2. Prérequis

Avant de commencer, assure-toi d’avoir installé :

- **Python 3.10+**
- **Docker Desktop**
- **Docker Compose**
- **Git**

---

## 3. Installation du projet

### 3.1. Cloner le dépôt
```bash
git clone https://github.com/<ton-utilisateur>/iphone-sentiment-analysis.git
cd iphone-sentiment-analysis
```

### 3.2. Créer et activer un environnement virtuel
```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3.3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

Le fichier `requirements.txt` contient :
- **FastAPI / Uvicorn** → pour l’API d’analyse
- **Transformers / Torch** → pour le modèle DistilBERT
- **Elasticsearch** → pour la connexion au cluster
- **Pandas / NLTK / Regex** → pour le traitement des données
- **TextBlob (optionnel)** → pour tests ou fallback

---

## 4. Préparation du dataset

### 4.1. Télécharger les données
Télécharge le dataset **[iPhone Customer Reviews NLP – Kaggle](https://www.kaggle.com/datasets/mrmars1010/iphone-customer-reviews-nlp)**  
et place le fichier `.csv` dans :
```
data/raw/
```

### 4.2. Nettoyage et conversion du dataset

Exécute le script :
```bash
python data/convert_kaggle_iphone_reviews.py
```
Ce script :
- charge le CSV Kaggle,  
- extrait le texte des avis (`reviewDescription`),  
- convertit les dates au bon format,  
- crée un fichier JSONL :  
  ```
  data/iphone_reviews.jsonl
  ```

### 4.3. Enrichissement des données

Exécute ensuite :
```bash
python data/enrich_dataset.py
```
Ce script ajoute deux champs :
- `source` → choisie aléatoirement parmi *Apple, Amazon, Fnac, eBay, Reddit, Twitter, YouTube, Blog...*  
- `country` → aléatoirement parmi *France, Germany, USA, Canada, India, China, Spain, Italy, UK, Brazil...*

Il génère le fichier :
```
data/iphone_reviews_enriched.jsonl
```

---

## 5. Déploiement de la stack Docker ELK

### 5.1. Lancer la stack
```bash
docker compose up -d
```

Cela démarre :
- **Elasticsearch** sur `localhost:9200`
- **Kibana** sur `localhost:5601`
- (optionnellement) **FastAPI** sur `localhost:8000`

### 5.2. Créer l’index Elasticsearch

Exécute le script :
```bash
bash es/scripts/create_index.sh
```
Ce script crée un index nommé `product_sentiment` avec le mapping suivant :
```json
{
  "author": {"type": "keyword"},
  "source": {"type": "keyword"},
  "country": {"type": "keyword"},
  "message": {"type": "text"},
  "sentiment_label": {"type": "keyword"},
  "sentiment_score": {"type": "float"},
  "created_at": {"type": "date"}
}
```

### 5.3. Charger les données enrichies
```bash
bash es/scripts/load_seed.sh data/iphone_reviews_enriched.jsonl
```
Vérifie que les données ont bien été indexées :
```bash
curl -X GET "http://localhost:9200/product_sentiment/_count"
```

---

## 6. Lancer le service d’analyse FastAPI

### 6.1. Démarrage
```bash
uvicorn app.app:app --host 0.0.0.0 --port 8000
```

### 6.2. Accéder à l’interface interactive
http://localhost:8000/docs

### 6.3. Exemple de requête
```bash
curl -X POST http://localhost:8000/analyze \
-H "Content-Type: application/json" \
-d '{"author": "user42", "source": "twitter", "message": "I love the new iPhone battery life!"}'
```

### 6.4. Exemple de réponse
```json
{
  "sentiment_label": "positive",
  "sentiment_score": 0.94,
  "timestamp": "2025-10-30T10:20:00"
}
```

---

## 7. Visualisation dans Kibana

### 7.1. Accéder à Kibana
http://localhost:5601

### 7.2. Créer une “Data View”
- Nom : `sentiment_s`
- Index : `product_sentiment`

### 7.3. Créer le dashboard
Visualisations recommandées :
- Histogramme temporel des sentiments (`created_at` groupé par `sentiment_label`)
- Donut chart : répartition globale des sentiments  
- KPI : moyenne de `sentiment_score`  
- Bar chart : `Average Sentiment by Source`  
- Bar chart : `Average Sentiment by Country`

### 7.4. Exporter ton dashboard
- `Stack Management → Saved Objects → Export NDJSON`
- Sauvegarde-le dans `/dashboards/sentiment_dashboard.ndjson`

---

## 8. Erreurs connues & solutions

| Problème | Cause probable | Solution |
|-----------|----------------|-----------|
| `docker not found` | Docker non installé / PATH manquant | Redémarre après installation |
| `no shard available` | Index mal initialisé | Supprime et relance `create_index.sh` |
| `Internal Server Error 500` | Version ES incompatible | Mets à jour `elasticsearch` Python en 8.x |
| Dates identiques | Mauvais parsing CSV | Corrigé dans `convert_kaggle_iphone_reviews.py` |
| Tag Cloud inutilisable | Kibana ne gère pas le text tokenisé | Documenté comme limitation dans le rapport |

---

## 9. Résultats principaux

- ~70 % d’avis positifs, 20 % négatifs, 10 % neutres  
- Score moyen global : **0.82** (≈ 4,1/5)  
- Légères différences selon la source et le pays  
- Points négatifs fréquents : batterie, prix, surchauffe  
- Tag Cloud exploré mais non abouti (limitations Kibana)

---

## 10. Améliorations possibles

- Utiliser un modèle **BERT multilingue**  
- Nettoyer le texte avant indexation (stop words, lemmatisation)  
- Héberger la stack ELK sur un serveur cloud  
- Collecter des données supplémentaires (Twitter, Reddit)  

---

## 11. Auteur

Projet réalisé dans le cadre du module **Seconde session d’évaluation** à **HETIC**  
par **Mathis Fonbonne** — année 2025.
