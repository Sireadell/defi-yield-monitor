import requests
from src.config import TELEGRAM_BOT_TOKEN

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
print("[*] Fetching updates...")
response = requests.get(url)
print("[HTTP]", response.status_code)
print("[JSON]", response.text)
