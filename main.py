import logging
import os
from amazon_client import get_items

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔍 Recupero articoli da Amazon...")

    # Legge le keyword dai secrets
    keywords_env = os.environ.get("KEYWORDS", "")
    keywords = [kw.strip() for kw in keywords_env.split(",") if kw.strip()]

    if not keywords:
        logger.error("❌ Nessuna keyword trovata nelle variabili d'ambiente (KEYWORDS).")
        return

    all_items = []
    for keyword in keywords:
        results = get_items(keyword)

        if not results:
            logger.warning(f"⚠️ Nessun articolo trovato per '{keyword}'")
            continue

        # Mostra i titoli degli articoli trovati
        logger.info(f"📦 {len(results)} articoli trovati per '{keyword}':")
        for item in results:
            title = item.get("title") or "❓ Titolo non disponibile"
            logger.info(f"   - {title}")

        all_items.extend(results)

    if not all_items:
        logger.info("ℹ️ Nessun articolo trovato in totale.")
        return

    logger.info(f"✅ Totale articoli trovati: {len(all_items)}")

    # Qui puoi aggiungere il codice per inviare a Telegram
    # send_to_telegram(all_items)

if __name__ == "__main__":
    main()
