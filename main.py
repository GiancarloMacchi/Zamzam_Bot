import logging
import os
import json
from amazon_client import get_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")

    # Legge KEYWORDS dalle secret
    keywords = os.getenv("KEYWORDS", "").split(",")
    keywords = [kw.strip() for kw in keywords if kw.strip()]

    # Legge RESOURCES dalle secret
    resources_env = os.getenv("AMAZON_RESOURCES", "[]")
    try:
        resources = json.loads(resources_env)
    except json.JSONDecodeError:
        logger.error("❌ Errore nel parsing di AMAZON_RESOURCES, uso lista vuota")
        resources = []

    if not keywords:
        logger.warning("⚠️ Nessuna keyword trovata nelle secret")
        return

    if not resources:
        logger.warning("⚠️ Nessuna risorsa trovata nelle secret")
        return

    total_items = []
    for keyword in keywords:
        logger.info(f"🔍 Chiamata Amazon API con keyword: {keyword}")
        try:
            items = get_items(keyword, resources)
            if items:
                total_items.extend(items)
            else:
                logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
        except Exception as e:
            logger.error(f"❌ Errore durante il recupero degli articoli: {e}")

    if not total_items:
        logger.info("ℹ️ Nessun articolo trovato in totale.")
    else:
        logger.info(f"✅ Trovati {len(total_items)} articoli in totale.")

if __name__ == "__main__":
    main()
