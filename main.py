from amazon_api import cerca_prodotti
from telegram_bot import invia_messaggio

def esegui_bot():
    parole_chiave = os.getenv("KEYWORDS", "").split(",")
    for keyword in parole_chiave:
        prodotti = cerca_prodotti(keyword.strip())
        for p in prodotti:
            titolo = p["title"]
            prezzo = p.get("price")
            prezzo_scontato = p.get("discounted_price", prezzo)
            categoria = p.get("category", "")
            messaggio = (
                f"📦 {titolo}\n"
                f"Categoria: {categoria}\n"
                f"💰 Prezzo originale: €{prezzo}\n"
                f"🔥 Prezzo scontato: €{prezzo_scontato}\n"
            )
            invia_messaggio(messaggio)

if __name__ == "__main__":
    esegui_bot()
