import sys
from telegram_bot import send_message

def test_telegram_connection():
    """
    Manda un messaggio di test a Telegram per verificare che il bot funzioni.
    """
    print("🔍 Verifica connessione a Telegram...")
    if send_message("✅ Test di connessione a Telegram riuscito!"):
        print("Connessione OK!")
        return True
    else:
        print("❌ Errore di connessione a Telegram. Controlla TOKEN e CHAT_ID.")
        return False

def main():
    """
    Esecuzione principale del bot.
    """
    # 1️⃣ Test connessione
    if not test_telegram_connection():
        sys.exit(1)  # Ferma l'esecuzione se il test fallisce

    # 2️⃣ Qui aggiungerai la logica del bot
    print("🚀 Avvio operazioni principali...")
    send_message("💡 Il bot ora è attivo e funzionante!")

if __name__ == "__main__":
    main()
