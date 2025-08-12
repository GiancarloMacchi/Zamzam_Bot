# main.py
import logging
import sys
from utils import (
    setup_logger,
    get_config,
    check_required_config,
    search_amazon_products,
    qualifies_for_posting,
    make_message_for_product,
    send_telegram_message,
)

logger = setup_logger()

def esegui_bot():
    cfg = get_config()
    missing = check_required_config(cfg)
    if missing:
        logger.error("Errore: variabili mancanti: %s", ", ".join(missing))
        sys.exit(1)

    keywords = [k.strip() for k in (cfg.get("KEYWORDS") or "").split(",") if k.strip()]
    if not keywords:
        logger.info("Nessuna keyword nel .env: uso valori default")
        keywords = ["bambino", "bambini", "infanzia", "mamma", "gioco", "giocattolo", "scuola", "libro"]

    total_sent = 0
    for kw in keywords:
        logger.info("🔎 Ricerca di '%s' su Amazon...", kw)
        try:
            products = search_amazon_products(cfg, kw)
        except Exception as e:
            logger.exception("ERROR - Amazon API error: %s", e)
            continue

        if not products:
            logger.info("Nessun prodotto trovato per '%s'", kw)
            continue

        # gestiamo diversi formati (lista/dict)
        if hasattr(products, "get") and not isinstance(products, (list, tuple)):
            products = products.get("items") or products.get("Items") or []

        for p in products:
            try:
                if not qualifies_for_posting(p, cfg):
                    continue
                message = make_message_for_product(p, cfg)
                ok = send_telegram_message(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"], message)
                if ok:
                    total_sent += 1
            except Exception:
                logger.exception("Errore nella gestione prodotto: %s", p.get("title"))
                continue

    logger.info("Invio completato ✅ - Totale messaggi inviati: %d", total_sent)

if __name__ == "__main__":
    esegui_bot()
