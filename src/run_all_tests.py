# File: src/run_all_tests.py
import asyncio
from datetime import datetime
from src.services.llama import fetch_yields
from src.models.pool_model import PoolModel
from src.db.crud import save_pool
from src.test_setup import init_test_db, SessionLocal

async def run_tests():
    # Step 1: Initialize DB
    try:
        init_test_db()
        print("Test DB initialized.")
    except Exception as e:
        print("DB init error:", e)

    # Step 2: Fetch pools
    try:
        pools = await fetch_yields()
        print(f"Fetched {len(pools)} pools")
    except Exception as e:
        print("Fetch error:", e)
        pools = []

    # Step 3: Save pools
    errors = []
    session = SessionLocal()
    for d in pools:
        try:
            pool_id = d.get("pool_id") or f"{d.get('project','unknown')}_{d.get('chain','unknown')}"
            pool = PoolModel(
                pool_id=pool_id,
                protocol=d.get("project", "unknown"),
                chain=d.get("chain", "unknown"),
                apy=d.get("apy", 0.0),
                tvl=d.get("tvl_usd", 0.0),
                last_updated=datetime.utcnow()
            )
            save_pool(session, pool)
        except Exception as inner:
            # Rollback the session to continue with next pool
            session.rollback()
            error_msg = f"Error saving pool {pool_id}: {inner}"
            print(error_msg)
            errors.append(error_msg)

    print("\nPools processed.")
    if errors:
        print(f"\nTotal errors: {len(errors)}")
        for err in errors:
            print(err)
    else:
        print("All pools saved successfully.")

if __name__ == "__main__":
    asyncio.run(run_tests())
