import json, random

# Listes aléatoires
sources = ["apple", "amazon", "fnac", "bestbuy", "cdiscount", "ebay", "reddit", "twitter", "youtube", "blog"]
countries = ["France", "Germany", "USA", "Canada", "India", "China", "Australia", "Spain", "Italy", "UK", "Brazil", "Mexico"]

input_path = "data/iphone_reviews.jsonl"
output_path = "data/iphone_reviews_enriched.jsonl"

count = 0

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        doc = json.loads(line.strip())

        # Ajoute un pays et une source aléatoires
        doc["country"] = random.choice(countries)
        doc["source"] = random.choice(sources)

        outfile.write(json.dumps(doc, ensure_ascii=False) + "\n")
        count += 1

print(f" {count} documents enrichis et sauvegardés dans {output_path}")
