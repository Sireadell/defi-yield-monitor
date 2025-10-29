import sys, os
# Add project root to sys.path so "src.*" imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
import requests
from src.alerts import handle_command, send_telegram_alert
from src.config import TELEGRAM_BOT_TOKEN

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
POLL_TIMEOUT = 60  # seconds
MY_CHAT_ID = "1255715938"  # your chat ID for startup alerts

print(f"[DEBUG] Executing file: {os.path.abspath(__file__)}")
print(f"[DEBUG] sys.path: {sys.path}")

def get_updates(offset=None):
    params = {"timeout": POLL_TIMEOUT, "allowed_updates": ["message"]}
    if offset:
        params["offset"] = offset
    try:
        resp = requests.get(API_URL + "getUpdates", params=params, timeout=POLL_TIMEOUT + 10)
        return resp.json()
    except Exception as e:
        print(f"[ERROR] getUpdates failed: {e}")
        return {"ok": False, "result": []}

def main():
    print("[BOT] Listener started...")

    # Send startup message
    try:
        send_telegram_alert("Bot started! Send /start to test.", MY_CHAT_ID)
        print("[DEBUG] Startup alert sent successfully")
    except Exception as e:
        print(f"[ERROR] Failed to send startup alert: {e}")

    # Initialize offset to avoid old messages
    offset = None
    data = get_updates()
    if data.get("ok") and data.get("result"):
        offset = data["result"][-1]["update_id"] + 1

    while True:
        data = get_updates(offset)
        if not data.get("ok"):
            print("[ERROR] Telegram API not ok")
            time.sleep(5)
            continue

        results = data.get("result", [])
        if not results:
            time.sleep(1)
            continue

        for update in results:
            offset = update["update_id"] + 1
            msg = update.get("message")
            if not msg:
                continue

            chat_id = str(msg["chat"]["id"])
            text = (msg.get("text") or "").strip()

            try:
                if text.lower() == "/start":
                    send_telegram_alert(
                        "<b>DeFi Yield Monitor</b>\n\n"
                        "Live APY & TVL tracking\n\n"
                        "<b>Commands:</b>\n"
                        "/top — Top 5 pools\n"
                        "/eth /polygon /arbitrum\n"
                        "/base /bsc /optimism",
                        chat_id
                    )
                elif text.startswith("/"):
                    resp = handle_command(text, chat_id)
                    if resp:
                        send_telegram_alert(resp, chat_id)
            except Exception as e:
                print(f"[ERROR] Failed to handle message '{text}' for chat {chat_id}: {e}")

        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped by user")
    except Exception as e:
        print(f"[ERROR] Fatal error in main: {e}")
