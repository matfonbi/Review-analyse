#!/usr/bin/env bash
set -euo pipefail

ES="${ES_HOST:-http://localhost:9200}"
FILE=${1:-data/seed.jsonl}

echo "Chargement du fichier $FILE dans Elasticsearch ($ES)..."
while IFS= read -r line; do
  curl -s -H "Content-Type: application/json" -X POST "$ES/sentiment_s/_doc" -d "$line" > /dev/null
done < "$FILE"

echo " Données chargées avec succès."