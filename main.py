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
)

# il search_amazon_products è definito in amazon_api.py — utils importerà amazon_api

logging.basicConfig(
    level=logging.INFO,
    format="***%d-%m-%*** %H:%M:%S,%f - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def esegui_bot():
    cfg = get_config()
    missing = check_required_config(cfg)
    if missing:
        logger.error("Errore: una o più variabili d'ambiente mancanti: %s", ", ".join(missing))
        sys.exit(1)

    keywords = [k.strip() for k in (cfg.get("KEYWORDS") or "").split(",") if k.strip()]
    if not keywords:
        logger.info("Nessuna keyword fornita, uso lista di default interna.")
        keywords = ["bambino", "bambini", "mamma", "neonato", "gioco", "giocattolo", "scuola", "libro"]

    total_sent = 0

    for kw in keywords:
        logger.info("🔎 Searching '%s' on Amazon.it", kw)
        try:
            # search_amazon_products è in amazon_api.py, utils lo richiama dinamicamente
            from amazon_api import search_amazon_products  # import locale per evitare circolarità
            products = search_amazon_products(kw)
        except Exception as e:
            logger.error("ERROR - Amazon API error: %s", e)
            continue

        if not products:
            logger.info("Nessun prodotto trovato per '%s'", kw)
            continue

        # prodotti potrebbe essere lista di items
        for p in products:
            try:
                if not qualifies_for_posting(p, cfg):
                    continue

                message = make_message_for_product(p, cfg)
                ok = send_telegram_message(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"], message)
                if ok:
                    total_sent += 1
            except Exception as e:
                logger.exception("Errore nella gestione prodotto: %s", e)
                # continua

    logger.info("Invio completato ✅ - Totale messaggi inviati: %d", total_sent)


if __name__ == "__main__":
    esegui_bot()
