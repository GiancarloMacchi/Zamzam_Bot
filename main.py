import os
from utils import cerca_prodotti, KEYWORDS
import telegram

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MIN_SAVE = int(os.getenv("MIN_SAVE", 30))

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def main():
    for keyword in KEYWORDS:
        prodotti = cerca_prodotti(keyword)
        for p in prodotti:
            try:
                if p["risparmio"] and "%" in p["risparmio"]:
                    # Estrae solo numero percentuale
                    percent = int("".join(filter(str.isdigit, p["risparmio"])))
                    if percent < MIN_SAVE:
                        continue

                messaggio = f"🔍 *{p['titolo']}*\n💰 Prezzo: {p['prezzo']}\n" \
                            f"💸 Risparmio: {p['risparmio']}\n🔗 [Acquista qui]({p['url']})"
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=messaggio, parse_mode="Markdown")
            except Exception as e:
                print(f"Errore invio Telegram: {e}")

if __name__ == "__main__":
    main()
