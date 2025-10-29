# src/bot_listener.py
import time
import requests
from src.alerts import handle_command, send_telegram_alert
from src.config import TELEGRAM_BOT_TOKEN

def start_bot_listener():
    print("[Bot] Listener started. Type /ethereum, etc.")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            res = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=40)
            data = res.json()
            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = str(msg.get("chat", {}).get("id"))

                if text == "/start":
                    send_telegram_alert(
                        "<b>DeFi Spike Monitor</b>\n\n"
                        "I'll alert you on spikes!\n\n"
                        "<b>Commands:</b>\n"
                        "/ethereum /arbitrum /polygon /optimism /base /bsc /avalanche /top",
                        chat_id
                    )
                    continue

                if text.startswith("/"):
                    response = handle_command(text, chat_id)
                    if response:
                        send_telegram_alert(response, chat_id)
        except:
            time.sleep(5)