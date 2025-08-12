import os
from telegram_bot import send_message

def main():
    """
    Esempio di esecuzione principale del bot.
    """
    messaggio = "Ciao! Il bot è attivo e funzionante ✅"
    inviato = send_message(messaggio)

    if inviato:
        print("Messaggio inviato con successo.")
    else:
        print("Errore nell'invio del messaggio.")

if __name__ == "__main__":
    main()
