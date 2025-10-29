import requests
from decouple import config

# Load from .env
TOKEN = config('TELEGRAM_BOT_TOKEN')
CHAT_ID = config('TELEGRAM_CHAT_ID', cast=int)

# API endpoint
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

# Message
payload = {
    "chat_id": CHAT_ID,
    "text": "Python send test successful! Token works in code too.",
    "parse_mode": "HTML"
}

# Send
response = requests.post(url, json=payload, timeout=10)
print(response.json())