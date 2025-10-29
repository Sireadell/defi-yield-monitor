import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

DATABASE_URL = "sqlite:///src/db/pools.db"

SPIKE_APY_THRESHOLD = 0.025  # 2.5%
SPIKE_TVL_THRESHOLD = 0.030  # 3%

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("[CONFIG] Bot token loaded:", bool(TELEGRAM_BOT_TOKEN))