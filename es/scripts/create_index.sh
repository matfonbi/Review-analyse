#!/usr/bin/env bash
set -euo pipefail

ES="${ES_HOST:-http://localhost:9200}"

echo "Création de l’index product_sentiment..."
curl -X PUT "$ES/product_sentiment" \
  -H "Content-Type: application/json" \
  -d @$(dirname "$0")/../mappings/product_sentiment.mapping.json

echo
echo "Ajout de l’alias sentiment_s..."
curl -X POST "$ES/_aliases" -H "Content-Type: application/json" -d '{
  "actions": [
    {"add": {"index": "product_sentiment", "alias": "sentiment_s"}}
  ]
}'
echo
echo "Index et alias créés avec succès."
