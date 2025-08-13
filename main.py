import os
from dotenv import load_dotenv
from amazon_client import get_items
from telegram_bot import send_telegram_message

load_dotenv()

RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"

def main():
    items = get_items()
    if not items:
        send_telegram_message("❌ Nessuna offerta trovata o errore nelle API Amazon.")
        return

    for item in items:
        message = (
            f"📦 <b>{item['title']}</b>\n"
            f"💰 Prezzo: {item['price']} {item['currency']}\n"
            f"💸 Sconto: {item['saving']}%\n"
            f"🔗 <a href='{item['url']}'>Vai all'offerta</a>"
        )
        send_telegram_message(message, parse_mode="HTML")

if __name__ == "__main__":
    if RUN_ONCE:
        main()
    else:
        # se in futuro vuoi farlo girare ciclicamente puoi inserire un loop qui
        main()
