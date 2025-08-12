# main.py
import os
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    cfg = get_config()

    missing = check_required_config(cfg)
    if missing:
        logger.error("Errore: una o più variabili d'ambiente mancanti: %s", ", ".join(missing))
        # Exit with non-zero to make l'Action fallire e mostrarti l'errore
        sys.exit(1)

    keywords = [k.strip() for k in cfg["KEYWORDS"].split(",") if k.strip()] if cfg["KEYWORDS"] else []
    if not keywords:
        logger.info("Nessuna keyword fornita, uso lista di default interna.")
        keywords = ["bambino", "bambini", "mamma", "neonato", "gioco", "giocattolo", "scuola", "libro"]

    total_sent = 0

    # Per ogni keyword cerco prodotti
    for kw in keywords:
        logger.info("🔎 Searching '%s' on Amazon.it", kw)
        try:
            products = search_amazon_products(cfg, kw)
        except Exception as e:
            logger.error("ERROR - Amazon API error: %s", e)
            # Continua con la prossima keyword
            continue

        if not products:
            logger.info("Nessun prodotto trovato per '%s'", kw)
            continue

        # Se la struttura del risultato è singola (non iterabile) gestisco lo stesso
        if hasattr(products, "get") and not isinstance(products, (list, tuple)):
            # se è un dict con Items dentro
            products = products.get("Items") or products.get("items") or []

        for p in products:
            try:
                # Salta prodotti senza offerte
                if not qualifies_for_posting(p, cfg):
                    # la funzione di logging già scrive perché è stato scartato
                    continue

                # Componi il messaggio e invia
                message = make_message_for_product(p, cfg)
                send_telegram_message(cfg["TELEGRAM_BOT_TOKEN"], cfg["TELEGRAM_CHAT_ID"], message)
                total_sent += 1

            except Exception as e:
                logger.exception("Errore nella gestione prodotto: %s", e)
                # Continua con il prossimo prodotto

    logger.info("Invio completato ✅ - Totale messaggi inviati: %d", total_sent)


if __name__ == "__main__":
    main()
