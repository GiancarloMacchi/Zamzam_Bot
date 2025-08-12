# run-bot.py
# Avvia il bot su GitHub Actions

try:
    from main import esegui_bot
except ImportError:
    # Se esegui_bot non esiste, importa semplicemente main
    import main
    if __name__ == "__main__":
        pass  # main.py si eseguirà direttamente
else:
    if __name__ == "__main__":
        esegui_bot()
