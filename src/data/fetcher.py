import requests
from src.db.models import PoolModel
from datetime import datetime

def fetch_sample_pool():
    """Fetch one mock pool from DefiLlama API for test."""
    url = "https://yields.llama.fi/pools"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()["data"][0]
    return PoolModel(
        pool_id=data["pool"],
        protocol=data["project"],
        chain=data["chain"],
        apy=data.get("apy", 0.0),
        tvl=data.get("tvlUsd", 0.0),
        last_updated=datetime.utcnow(),
    )
