from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from elasticsearch import Elasticsearch
from transformers import pipeline
import os
from typing import List



# --- Config ---
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
es = Elasticsearch(ES_HOST)
sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

app = FastAPI(title="iPhone 17 Sentiment Analyzer")

# --- Schéma d'entrée ---
class AnalyzeIn(BaseModel):
    author: str
    source: str
    message: str

# --- Schéma de sortie ---
class AnalyzeOut(BaseModel):
    sentiment_label: str
    sentiment_score: float
    indexed_id: str
    created_at: str

class BulkAnalyzeIn(BaseModel):
    messages: List[AnalyzeIn]  # liste de messages à analyser

# --- Fonction d'analyse ---
@app.post("/analyze", response_model=AnalyzeOut)
def analyze(data: AnalyzeIn):
    result = sentiment_model(data.message)[0]
    label = result["label"].lower()
    score = float(result["score"])

    # ajout logique "neutre" si confiance faible
    if 0.45 <= score <= 0.55:
        label = "neutral"

    doc = {
        "author": data.author,
        "source": data.source,
        "message": data.message,
        "sentiment_label": label,
        "sentiment_score": score,
        "created_at": datetime.utcnow().isoformat()
    }

    res = es.index(index="sentiment_s", document=doc)
    return AnalyzeOut(
        sentiment_label=label,
        sentiment_score=score,
        indexed_id=res["_id"],
        created_at=doc["created_at"]
    )


@app.post("/bulk_analyze")
def bulk_analyze(data: BulkAnalyzeIn):
    results = []
    for msg in data.messages:
        # Analyse du texte
        result = sentiment_model(msg.message)[0]
        label = result["label"].lower()
        score = float(result["score"])
        if 0.45 <= score <= 0.55:
            label = "neutral"

        doc = {
            "author": msg.author,
            "source": msg.source,
            "message": msg.message,
            "sentiment_label": label,
            "sentiment_score": score,
            "created_at": datetime.utcnow().isoformat()
        }

        # Envoi dans Elasticsearch
        es.index(index="sentiment_s", document=doc)

        results.append({
            "author": msg.author,
            "source": msg.source,
            "sentiment_label": label,
            "sentiment_score": score
        })

    return {"analyzed_count": len(results), "results": results}


# route de test
@app.get("/")
def root():
    return {"status": "FastAPI with HuggingFace is running"}
