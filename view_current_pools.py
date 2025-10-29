# src/view_current_pools.py

from src.db.session import get_db
from src.db.models import PoolModel

def view_pools():
    with get_db() as db:
        pools = db.query(PoolModel).all()
        if not pools:
            print("No pools found in the database.")
            return

        print(f"Found {len(pools)} pools:\n")
        for pool in pools:
            print(f"ID: {pool.id}, Name: {pool.name}, TVL: {pool.tvl}, APR: {pool.apr}, Created At: {pool.created_at}")

if __name__ == "__main__":
    view_pools()
