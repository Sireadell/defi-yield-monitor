import asyncio
import logging
from src.db.base import Base
from src.db.models import PoolModel
from src.data.fetcher import fetch_sample_pool
from src.spike_detector import detect_spikes, log_spikes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL

# === DB Setup ===
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_pool(db, pool_data):
    """Simple upsert for PoolModel instance"""
    existing = db.query(PoolModel).filter(PoolModel.pool_id == pool_data.pool_id).first()
    if existing:
        existing.apy = pool_data.apy
        existing.tvl = pool_data.tvl
        existing.protocol = pool_data.protocol
        existing.chain = pool_data.chain
        existing.last_updated = pool_data.last_updated
    else:
        db.add(pool_data)
    db.commit()


async def main_loop():
    while True:
        try:
            logger.info("Fetching latest pool data from DefiLlama...")
            new_pool = fetch_sample_pool()

            with SessionLocal() as db:
                save_pool(db, new_pool)

                # Detect spikes and get recent pools
                spikes, recent_pools = detect_spikes(db, lookback_hours=24)

                # Pass both to logger
                log_spikes(spikes, recent_pools)

        except Exception as e:
            logger.error(f"Error in loop: {e}")

        logger.info("Sleeping 15 minutes until next check...")
        await asyncio.sleep(900)  # 15 minutes


if __name__ == "__main__":
    asyncio.run(main_loop())