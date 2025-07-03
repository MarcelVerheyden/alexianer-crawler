import requests
from bs4 import BeautifulSoup
import hashlib
import os
import re

URL = "https://www.alexianer-krefeld.de/leistungen/kliniken/klinik-fuer-psychische-gesundheit/allgemeinpsychiatrie/fachambulanz-adhs"
STATE_FILE = "last_hash.txt"
CHECK_PHRASE = "Eine Aufnahme auf die Warteliste kann daher zur Zeit nicht erfolgen"

def fetch_page():
    response = requests.get(URL)
    response.raise_for_status()
    return response.text

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    target_div = soup.find("div", id="c53864")
    if not target_div:
        return ""

    ce_text_div = target_div.find("div", class_="ce-text")
    if not ce_text_div:
        return ""

    text = ce_text_div.get_text(separator=" ", strip=True)
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

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

    print("---- Extracted Text ----")
    print(repr(text))
    print("------------------------")

    last_hash = read_last_hash()
    current_hash = compute_hash(text)

    if current_hash != last_hash:
        if CHECK_PHRASE not in text:
            send_telegram("✅ Die Aufnahme auf die Warteliste ist wieder möglich! Bitte prüfen Sie die Webseite: " + URL)
        else:
            send_telegram("ℹ️ Es gab eine Änderung, aber der Satz ist weiterhin vorhanden.")
        save_hash(current_hash)
    else:
        send_telegram("ℹ️ Keine Änderung seit dem letzten Check.")

if __name__ == "__main__":
    main()
