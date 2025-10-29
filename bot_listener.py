# bot_listener.py
import os
import sys
import signal
import logging
from typing import Optional
import asyncio

# === Fix path for Windows & imports ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from src.config import TELEGRAM_BOT_TOKEN
from src.alerts import handle_command, send_telegram_alert
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# === Logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger(__name__)

# === Global app reference ===
application: Optional[Application] = None


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all bot commands: /top, /eth, /stats, etc."""
    if not update.effective_message:
        return
    cmd = update.effective_message.text or ""
    chat_id = str(update.effective_chat.id)

    try:
        # Run blocking DB + HTTP in thread pool
        response = await asyncio.to_thread(handle_command, cmd, chat_id)
        await update.effective_message.reply_html(response)
    except Exception as e:
        log.error(f"Command '{cmd}' failed: {e}")
        await update.effective_message.reply_text("Error. Try again later.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with help."""
    if not update.effective_message:
        return
    await update.effective_message.reply_html(
        "<b>DeFi Yield Monitor</b>\n\n"
        "Live APY & TVL tracking across chains.\n\n"
        "<b>Commands:</b>\n"
        "/top — Global top 5\n"
        "/eth /polygon /arbitrum /base /bsc /optimism\n"
        "/stats — Network stats\n\n"
        "<i>Fresh data • Powered by xAI</i>"
    )


def auto_alert_job():
    """Send /top to channel every 6 hours."""
    CHANNEL_ID = "-1001234567890"  # ← CHANGE TO YOUR CHANNEL ID
    msg = handle_command("/top", CHANNEL_ID)
    header = f"Auto Alert • {datetime.datetime.now().strftime('%b %d, %H:%M UTC')}"
    send_telegram_alert(f"<b>{header}</b>\n\n{msg}", CHANNEL_ID)


def signal_handler(signum, frame):
    """Graceful shutdown."""
    log.info("Shutting down bot...")
    if application and application.running:
        asyncio.create_task(application.stop())
    sys.exit(0)


def main():
    global application

    if not TELEGRAM_BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN missing!")
        return

    # === Build app ===
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # === Command handlers ===
    commands = [
        "top", "eth", "ethereum", "polygon", "poly",
        "arbitrum", "arb", "base", "bsc", "binance",
        "optimism", "op", "stats"
    ]
    for cmd in commands:
        application.add_handler(CommandHandler(cmd, command_handler))

    application.add_handler(CommandHandler("start", start_command))

    # === Auto-alert scheduler ===
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        auto_alert_job,
        'interval',
        hours=6,
        next_run_time=datetime.datetime.now()
    )
    scheduler.start()
    log.info("Auto-alert scheduled every 6 hours")

    # === Graceful shutdown ===
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # === Start polling ===
    log.info("Bot started. Polling...")
    try:
        application.run_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True,  # Clean start
            allowed_updates=Update.ALL_TYPES
        )
    except Exception as e:
        log.exception(f"Polling crashed: {e}")
    finally:
        log.info("Bot stopped.")


if __name__ == "__main__":
    main()