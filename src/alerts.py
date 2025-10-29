# src/alerts.py
import requests
import logging
from src.config import TELEGRAM_BOT_TOKEN, DATABASE_URL
from src.db.models import PoolModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)
SessionLocal = sessionmaker(bind=engine)


def send_telegram_alert(message: str, chat_id: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        log.error("Telegram config missing")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    for i in range(3):
        try:
            r = requests.post(url, data=payload, timeout=10)
            if r.status_code == 200:
                log.info("Telegram alert sent")
                return True
            log.warning(f"Telegram error {r.status_code}: {r.text}")
        except Exception as e:
            log.error(f"Send attempt {i+1} failed: {e}")
    return False


def handle_command(command: str, chat_id: str) -> str:
    cmd = command.strip().lower().lstrip("/")
    session = SessionLocal()
    try:
        # ---- /top -------------------------------------------------
        if cmd == "top":
            pools = (
                session.query(PoolModel)
                .order_by(PoolModel.apy.desc())
                .limit(5)
                .all()
            )
            if not pools:
                return "No pools in DB."

            lines = ["<b>Top 5 Pools (Global)</b>"]
            for p in pools:
                protocol = getattr(p, "protocol", "Unknown")
                chain = getattr(p, "chain", "unknown").upper()
                apy = getattr(p, "apy", 0.0)
                lines.append(f"• <b>{protocol}</b> ({chain}): <b>{apy:.2f}%</b>")
            return "\n".join(lines)

        # ---- Chain commands ----------------------------------------
        chain_map = {
            "eth": "ethereum", "ethereum": "ethereum",
            "polygon": "polygon", "poly": "polygon",
            "arbitrum": "arbitrum", "arb": "arbitrum",
            "base": "base",
            "bsc": "bsc", "binance": "bsc",
            "optimism": "optimism", "op": "optimism",
        }

        if cmd in chain_map:
            chain_name = chain_map[cmd]
            pools = (
                session.query(PoolModel)
                .filter(PoolModel.chain.ilike(chain_name))
                .order_by(PoolModel.apy.desc())
                .limit(5)
                .all()
            )
            if not pools:
                return f"No pools on <b>{chain_name.title()}</b>."

            lines = [f"<b>{chain_name.title()} — Top 5</b>"]
            for p in pools:
                protocol = getattr(p, "protocol", "Unknown")
                apy = getattr(p, "apy", 0.0)
                lines.append(f"• <b>{protocol}</b>: <b>{apy:.2f}%</b>")
            return "\n".join(lines)

        # ---- Help --------------------------------------------------
        chains = ", ".join([f"/{c}" for c in {"eth", "polygon", "arbitrum", "base", "bsc", "optimism"}])
        return f"<b>Commands:</b>\n/top\n{chains}"

    except Exception as e:
        log.exception("handle_command error")
        return f"Error: {e}"
    finally:
        session.close()