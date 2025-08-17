import json
import os

CONFIG_FILE = "config.json"

def load_config():
    # Se usi Secrets di GitHub, puoi fare l'override con le variabili d'ambiente
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

    # Conversione DRY_RUN in booleano (può essere stringa o booleano)
    dry_run = config.get("DRY_RUN", True)
    if isinstance(dry_run, str):
        dry_run = dry_run.lower() == "true"
    config["DRY_RUN"] = dry_run

    # Assicuriamoci che KEYWORDS sia sempre lista
    keywords = config.get("KEYWORDS", [])
    if isinstance(keywords, str):
        keywords = [kw.strip() for kw in keywords.split(",")]
    config["KEYWORDS"] = keywords

    return config
