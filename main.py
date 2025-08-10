name: Run Amazon Bot

on:
  workflow_dispatch:      # avvio manuale
  schedule:
    - cron: "0 * * * *"   # ogni ora

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v3

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: 📦 Install dependencies
        run: pip install -r requirements.txt

      - name: 🔎 Debug env presence (no secret values are printed)
        env:
          AMAZON_ACCESS_KEY: ${{ secrets.AMAZON_ACCESS_KEY }}
          AMAZON_SECRET_KEY: ${{ secrets.AMAZON_SECRET_KEY }}
          AMAZON_ASSOCIATE_TAG: ${{ secrets.AMAZON_ASSOCIATE_TAG }}
          AMAZON_COUNTRY: ${{ secrets.AMAZON_COUNTRY }}
          BITLY_TOKEN: ${{ secrets.BITLY_TOKEN }}
          KEYWORDS: ${{ secrets.KEYWORDS }}
          MIN_SAVE: ${{ secrets.MIN_SAVE }}
          ITEM_COUNT: ${{ secrets.ITEM_COUNT }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          required=(AMAZON_ACCESS_KEY AMAZON_SECRET_KEY AMAZON_ASSOCIATE_TAG AMAZON_COUNTRY BITLY_TOKEN KEYWORDS MIN_SAVE ITEM_COUNT TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID)
          missing=()
          for v in "${required[@]}"; do
            if [ -z "${!v}" ]; then
              missing+=("$v")
            else
              echo "$v ✅"
            fi
          done
          if [ ${#missing[@]} -gt 0 ]; then
            echo "::error::Missing secrets: ${missing[*]}"
            exit 1
          else
            echo "All required secrets present."
          fi

      - name: 🚀 Run bot (one-shot)
        env:
          AMAZON_ACCESS_KEY: ${{ secrets.AMAZON_ACCESS_KEY }}
          AMAZON_SECRET_KEY: ${{ secrets.AMAZON_SECRET_KEY }}
          AMAZON_ASSOCIATE_TAG: ${{ secrets.AMAZON_ASSOCIATE_TAG }}
          AMAZON_COUNTRY: ${{ secrets.AMAZON_COUNTRY }}
          BITLY_TOKEN: ${{ secrets.BITLY_TOKEN }}
          KEYWORDS: ${{ secrets.KEYWORDS }}
          MIN_SAVE: ${{ secrets.MIN_SAVE }}
          ITEM_COUNT: ${{ secrets.ITEM_COUNT }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          RUN_ONCE: "true"   # IMPORTANT: in Actions vogliamo che termini dopo una chiamata
        run: python main.py
