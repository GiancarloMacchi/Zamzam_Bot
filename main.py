import os
import random
from amazon_api import cerca_prodotti
from bitlyshortener import Shortener
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Variabili da Repository Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
KEYWORDS = os.getenv("KEYWORDS", "").split(",")
MIN_SAVE = int(os.getenv("MIN_SAVE", 0))

bot = Bot(token=TELEGRAM_BOT_TOKEN)
shortener = Shortener(tokens=[BITLY_TOKEN], max_cache_size=256)

# Mappa categorie -> frasi simpatiche
FRASI_PER_CATEGORIA = {
    "infanzia": [
        "Un dolce pensiero per i piccoli tesori di casa! 🍼",
        "Perché crescere è un'avventura bellissima! 🌟"
    ],
    "bambino": [
        "Perfetto per i piccoli esploratori! 🚀",
        "Un sorriso assicurato per il tuo bimbo! 😄"
    ],
    "bambina": [
        "Un tocco di magia per la tua principessa! 👑",
        "Piccoli momenti, grandi ricordi! 💖"
    ],
    "mamma": [
        "Per rendere speciale ogni momento da mamma! ❤️",
        "Un aiuto in più per la super mamma di casa! 💪"
    ],
    "papà": [
        "Per il papà che ama viziare i suoi piccoli! 🎁",
        "Perché anche i papà meritano un sorriso! 😎"
    ],
    "giochi": [
        "Il divertimento è garantito! 🎲",
        "Perfetto per ore di allegria! 🤹"
    ],
    "giocattoli": [
        "Un nuovo compagno di giochi è arrivato! 🧸",
        "Risate e creatività senza fine! 🎨"
    ],
    "libri per bambini": [
        "Una nuova avventura da leggere insieme! 📚",
        "Per sognare ad occhi aperti! 🌙"
    ],
    "vestiti bambini": [
        "Stile e comfort per i più piccoli! 👕",
        "Pronti a correre e giocare con stile! 🏃"
    ],
    "vestiti bambina": [
        "Per la piccola fashionista di casa! 👗",
        "Eleganza e dolcezza in un solo vestito! 🌸"
    ],
    "premaman": [
        "Per vivere la gravidanza con il massimo comfort! 🤰",
        "Un abbraccio morbido per la futura mamma! 💕"
    ],
    "scuola": [
        "Pronti per un anno di successi! ✏️",
        "Per rendere lo studio più divertente! 📓"
    ],
    "asilo": [
        "Perfetto per i primi giorni di avventura scolastica! 🎒",
        "Piccoli passi verso grandi sogni! 🌈"
    ],
    "piscina": [
        "Tuffati nel divertimento! 🏊",
        "Pronti a nuotare come pesciolini! 🐠"
    ],
    "scarpe per bambini": [
        "Passi sicuri verso nuove avventure! 👟",
        "Perfette per correre verso la felicità! 🏃‍♂️"
    ],
    "videogiochi": [
        "Il divertimento è a portata di joystick! 🎮",
        "Nuove sfide ti aspettano! 🕹️"
    ]
}

# Frasi di fallback
FRASI_JOLLY = [
    "Un'occasione da non lasciarsi sfuggire! 🎯",
    "Lo volevi da tempo? Ora è il momento giusto! 💥",
    "Affrettati prima che finisca! ⏳"
]

def scegli_frase(titolo, descrizione=""):
    testo = f"{titolo} {descrizione}".lower()
    for categoria, frasi in FRASI_PER_CATEGORIA.items():
        if categoria.lower() in testo:
            return random.choice(frasi)
    return random.choice(FRASI_JOLLY)

def pubblica_offerte():
    prodotti = []
    for kw in KEYWORDS:
        prodotti.extend(cerca_prodotti(kw.strip(), item_count=5, min_save=MIN_SAVE))

    if not prodotti:
        print("Nessun prodotto trovato.")
        return

    for p in prodotti:
        short_url = shortener.shorten_urls([p["link"]])[0]
        frase = scegli_frase(p["titolo"], p.get("descrizione", ""))
        messaggio = (
            f"📦 {p['titolo']}\n"
            f"💰 Prezzo: {p['prezzo']}€\n"
            f"💸 Sconto: {p['sconto']}%\n"
            f"🔗 {short_url}\n\n"
            f"{frase}"
        )
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio)

if __name__ == "__main__":
    pubblica_offerte()
