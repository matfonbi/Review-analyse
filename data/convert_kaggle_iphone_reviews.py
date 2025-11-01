import pandas as pd
import json
from datetime import datetime

# --- Chargement du CSV Kaggle ---
print("📥 Chargement du dataset Kaggle...")
df = pd.read_csv("data/iphone.csv")

# --- Vérification basique ---
print(f"Nombre total d'avis : {len(df)}")

# --- Nettoyage : on garde uniquement les colonnes utiles ---
df = df[["date", "ratingScore", "reviewTitle", "reviewDescription", "variant"]]

# --- Construction des documents JSONL ---
print("🔄 Conversion en format JSONL...")
data = []
for i, row in df.iterrows():
    # Combine le titre et la description s’ils existent
    message = ""
    if pd.notna(row["reviewTitle"]):
        message += str(row["reviewTitle"]) + ". "
    if pd.notna(row["reviewDescription"]):
        message += str(row["reviewDescription"])

    # Gestion du score numérique
    score = float(row["ratingScore"]) / 5.0 if pd.notna(row["ratingScore"]) else 0.5

    # Définition du label
    if score >= 0.7:
        label = "positive"
    elif score <= 0.4:
        label = "negative"
    else:
        label = "neutral"

    # Gestion de la date
    from dateutil import parser

    try:
        created = parser.parse(str(row["date"]))  # détecte automatiquement le format
    except Exception:
        created = datetime.utcnow()  # fallback si la date est invalide


    data.append({
        "author": f"user_{i}",
        "source": "kaggle",
        "message": message.strip(),
        "sentiment_label": label,
        "sentiment_score": round(score, 3),
        "created_at": created.isoformat()
    })

# --- Sauvegarde ---
with open("data/iphone_reviews.jsonl", "w", encoding="utf-8") as f:
    for d in data:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print(f"✅ {len(data)} avis convertis et enregistrés dans data/iphone_reviews.jsonl")
