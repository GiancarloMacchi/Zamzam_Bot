# utils.py
import requests

def shorten_url(long_url, bitly_token):
    """
    Accorcia un URL usando l'API di Bitly.
    Ritorna l'URL accorciato o l'originale in caso di errore.
    """
    api_url = "https://api-ssl.bitly.com/v4/shorten"
    headers = {
        "Authorization": f"Bearer {bitly_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "long_url": long_url
    }

    try:
        r = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("link", long_url)
        else:
            print(f"Bitly error {r.status_code}: {r.text}")
            return long_url
    except Exception as e:
        print(f"Errore durante l'accorciamento URL: {e}")
        return long_url
