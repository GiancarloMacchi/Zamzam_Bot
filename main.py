import os
from amazon_api import cerca_prodotti
from telegram_bot import send_message
from dotenv import load_dotenv

load_dotenv()

KEYWORDS = os.getenv("KEYWORDS", "articoli infanzia, peluches, mamma, papà, libri bambini, vestiti bambini, scuola")
ITEM_COUNT = int(os.getenv("ITEM_COUNT", 10))
MIN_SAVE = int(os.getenv("MIN_SAVE", 20))  # Default 20%

def main():
    keyword_list = [kw.strip() for kw in KEYWORDS.split(",")]

    for keyword in keyword_list:
        prodotti = cerca_prodotti(keyword, ITEM_COUNT, MIN_SAVE)

        if not prodotti:
            send_message(f"Nessun prodotto trovato per '{keyword}' con sconto minimo {MIN_SAVE}%")
            continue

        for p in prodotti:
            messaggio = (
                f"**{p['titolo']}**\n"
                f"💰 Prezzo: {p['prezzo']} €\n"
                f"💸 Prezzo di listino: {p['prezzo_listino']} €\n"
                f"📉 Sconto: {p['sconto']}%\n"
                f"[🔗 Link all'offerta]({p['link']})"
            )
            if p.get("immagine"):
                messaggio += f"\n🖼 {p['immagine']}"

            send_message(messaggio)

if __name__ == "__main__":
    main()
