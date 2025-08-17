import json
import os

def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Sovrascrivi con le secrets / env variables se presenti
    config["AMAZON_ACCESS_KEY"] = os.getenv("AMAZON_ACCESS_KEY", config.get("AMAZON_ACCESS_KEY"))
    config["AMAZON_SECRET_KEY"] = os.getenv("AMAZON_SECRET_KEY", config.get("AMAZON_SECRET_KEY"))
    config["AMAZON_ASSOCIATE_TAG"] = os.getenv("AMAZON_ASSOCIATE_TAG", config.get("AMAZON_ASSOCIATE_TAG"))
    config["TELEGRAM_BOT_TOKEN"] = os.getenv("TELEGRAM_BOT_TOKEN", config.get("TELEGRAM_BOT_TOKEN"))
    config["TELEGRAM_CHAT_ID"] = os.getenv("TELEGRAM_CHAT_ID", config.get("TELEGRAM_CHAT_ID"))
    
    return config
