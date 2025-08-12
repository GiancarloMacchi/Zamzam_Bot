# main.py
import logging
import sys
from utils import (
    get_config,
    check_required_config,
    search_amazon_products,
    qualifies_for_posting,
    make_message_for_product,
    send_telegram_message,
    setup_logger,
)

setup_logger()
logger = logging.getLogger(__name__)


def esegui_bot():
    cfg = get_config()
    missing = check_required_config(cfg)
    if missing:
        logger.error("Errore: variabili mancanti: %s", ", ".join(missing))
        sys.exit(1)

    # keywords: se non presenti usa default italiano
    keywords = [k.strip() for k in cfg.get("KEYWORDS", "").split(",") if k.strip()] or [
        "bambino", "bambini", "infanzia", "mamma", "mamme", "gioco", "giocattolo", "scuola", "libro", "videogiochi", "genitori"
    ]

    total_sent = 0
    country = cfg.get("AMAZON_COUNTRY", "it")

    for kw in keywords:
        logger.info("🔎 Ricerca di '%s' su Amazon...", kw)
        try:
            products = search_amazon_products(kw, country)
        except Exception as e:
            logger.error("ERROR - Errore fetch Amazon per '%s': %s", kw, e)
            continue

        if not products:
            logger.info("Nessun prodotto trovato per '%s'", kw)
            continue

        # assicurarsi sia lista
        if hasattr(products, "get") and not isinstance(products, (list, tuple)):
            products = products.get("Items") or products.get("items") or []

        for p in products:
            try:
                if not qualifies_for_posting(p, cfg):
                    # qualifies_for_posting già fa logging quando scarta
                    continue

                message = make_message_for_product(p, cfg)
                send_telegram_message(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"], message)
                total_sent += 1

            except Exception as e:
                logger.exception("Errore nella gestione prodotto: %s", e)
                continue

    logger.info("Invio completato ✅ - Totale messaggi inviati: %d", total_sent)


if __name__ == "__main__":
    esegui_bot()
