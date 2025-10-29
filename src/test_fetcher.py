import asyncio
from datetime import datetime, timezone
from src.services.llama import fetch_yields
from src.models.pool_model import PoolModel
from src.db.crud import save_pool
from src.db.database import init_test_db, SessionLocal

async def main():
    # Initialize test DB
    init_test_db()

    # Fetch sample pools
    pools = await fetch_yields()
    print(f"Fetched {len(pools)} pools.")

    # Create DB session
    session = SessionLocal()

    try:
        for d in pools:
            pool_id = d.get("pool") or d.get("pool_id") or f"{d.get('project')}_{d.get('chain')}"
            pool = PoolModel(
                pool_id=pool_id,
                protocol=d.get("project") or d.get("protocol") or "unknown",
                chain=d.get("chain") or "unknown",
                apy=d.get("apy") or 0.0,
                tvl=d.get("tvlUsd") or d.get("tvl_usd") or 0.0,
                last_updated=datetime.now(timezone.utc)
            )
            save_pool(session, pool)
        print("✅ All pools saved successfully.")
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(main())
