import os
import json
from pathlib import Path

def _cast_int(v, default):
    try:
        return int(v)
    except Exception:
        return default

def _to_bool(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "y"}

def load_config():
    # Facoltativo: config da JSON (es. config.json) + override da ENV
    cfg_path = Path(os.getenv("APP_CONFIG_FILE", "config.json"))
    file_cfg = {}
    if cfg_path.exists():
        with cfg_path.open("r", encoding="utf-8") as f:
            file_cfg = json.load(f)

    def get(name, default=None, cast=None, required=False):
        v = os.getenv(name, file_cfg.get(name, default))
        if required and (v is None or v == ""):
            raise RuntimeError(f"Missing required setting: {name}")
        if cast:
            return cast(v)
        return v

    # KEYWORDS può essere lista nel JSON o stringa comma-separated in ENV
    keywords = file_cfg.get("KEYWORDS", os.getenv("KEYWORDS"))
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    if not keywords:
        keywords = ["regali bambino", "regali mamma"]  # default

    return {
        "AMAZON_ACCESS_KEY": get("AMAZON_ACCESS_KEY"),
        "AMAZON_SECRET_KEY": get("AMAZON_SECRET_KEY"),
        "AMAZON_ASSOCIATE_TAG": get("AMAZON_ASSOCIATE_TAG"),
        "AMAZON_COUNTRY": get("AMAZON_COUNTRY", "it"),
        "TELEGRAM_BOT_TOKEN": get("TELEGRAM_BOT_TOKEN", required=True),
        "TELEGRAM_CHAT_ID": get("TELEGRAM_CHAT_ID", required=True),
        "KEYWORDS": keywords,
        "MIN_SAVE": get("MIN_SAVE", 30, cast=lambda v: _cast_int(v, 30)),
        "ITEM_COUNT": get("ITEM_COUNT", 10, cast=lambda v: _cast_int(v, 10)),
        # Se usi la AmazonClient mock, meglio non inviare immagini fittizie
        "MOCK": get("MOCK", True, cast=_to_bool),
    }
