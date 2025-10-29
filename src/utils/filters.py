# src/utils/filters.py
from typing import List
from src.models.pool import Pool

def filter_spikes(pools: List[Pool], deposits: dict) -> List[Pool]:
    """
    Filter pools with APY > 10%, TVL > 10M, and deposits > 50k
    """
    return [
        pool for pool in pools
        if pool.apy > 10.0
        and pool.tvl > 10_000_000
        and deposits.get(pool.pool_id, 0) > 50_000
    ]
