import os
import json
import logging
from amazon_paapi import AmazonAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amazon_client")


def get_items(keyword):
    try:
        amazon = AmazonAPI(
            os.getenv("AMAZON_ACCESS_KEY"),
            os.getenv("AMAZON_SECRET_KEY"),
            os.getenv("AMAZON_ASSOCIATE_TAG"),
            os.getenv("AMAZON_COUNTRY"),
        )

        # Recupero risorse da secret AMAZON_RESOURCES
        resources_env = os.getenv("AMAZON_RESOURCES")
        if not resources_env:
            raise ValueError("⚠️ Variabile AMAZON_RESOURCES non trovata nelle Secret")

        try:
            resources = json.loads(resources_env)
            if not isinstance(resources, list):
                raise ValueError("AMAZON_RESOURCES deve essere una lista JSON")
        except json.JSONDecodeError as e:
            raise ValueError(f"AMAZON_RESOURCES non è un JSON valido: {e}")

        logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")

        items = amazon.search_items(
            keywords=keyword,
            item_count=int(os.getenv("ITEM_COUNT", 10)),
            resources=resources
        )

        # Salvo la risposta grezza per debug
        with open("amazon_debug.json", "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        logger.info("💾 amazon_debug.json salvato con le risposte grezze di Amazon")

        return items

    except Exception as e:
        logger.error(f"❌ Errore durante il recupero degli articoli: {e}")
        return []
