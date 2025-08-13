import json
import random
import os

# Carica le frasi dal file JSON
with open("phrases.json", "r", encoding="utf-8") as f:
    phrases = json.load(f)

def get_phrase(category):
    # Normalizza la categoria: minuscolo e senza spazi
    category = category.strip().lower()

    # Se la categoria non è nel JSON, prova a usare "default"
    if category not in phrases:
        category = "default"

    # Se ancora non esiste, ritorna una frase di fallback
    if category not in phrases:
        return "💥 Offerta imperdibile!"

    return random.choice(phrases[category])

# Esempio di utilizzo
keywords = json.loads(os.getenv("KEYWORDS", '["infanzia"]'))
for kw in keywords:
    print(get_phrase(kw))
