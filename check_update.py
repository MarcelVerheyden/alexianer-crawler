import requests
from bs4 import BeautifulSoup
import hashlib
import os

URL = "https://www.alexianer-krefeld.de/leistungen/kliniken/klinik-fuer-psychische-gesundheit/allgemeinpsychiatrie/fachambulanz-adhs"
TARGET_TEXT_SNIPPET = "wir derzeit keine neuen Termine in unserer Ambulanz vergeben"
STATE_FILE = "last_hash.txt"

def fetch_page():
    response = requests.get(URL)
    response.raise_for_status()
    return response.text

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    div = soup.find("div", class_="ce-text")
    return div.get_text(strip=True) if div else ""

def compute_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def read_last_hash():
    return open(STATE_FILE).read().strip() if os.path.exists(STATE_FILE) else ""

def save_hash(h):
    with open(STATE_FILE, "w") as f:
        f.write(h)

def send_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

def main():
    html = fetch_page()
    text = extract_text(html)
    current_hash = compute_hash(text)

    if TARGET_TEXT_SNIPPET not in text:
        send_telegram("⚠️ ADHS-Ambulanz Status hat sich geändert! Prüfe die Seite: " + URL)

    last_hash = read_last_hash()
    if current_hash != last_hash:
        send_telegram("🔄 Änderung erkannt auf der ADHS-Ambulanz Seite.")
        save_hash(current_hash)

if __name__ == "__main__":
    main()
