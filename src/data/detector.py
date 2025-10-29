from src.config import SPIKE_APY_THRESHOLD, SPIKE_TVL_THRESHOLD

def detect_spike(old_pool, new_pool):
    """Compare two pool states to detect spikes."""
    apy_diff = abs(new_pool.apy - old_pool.apy) / max(old_pool.apy, 1e-9)
    tvl_diff = abs(new_pool.tvl - old_pool.tvl) / max(old_pool.tvl, 1e-9)

    return {
        "apy_spike": apy_diff > SPIKE_APY_THRESHOLD,
        "tvl_spike": tvl_diff > SPIKE_TVL_THRESHOLD,
        "apy_change": apy_diff,
        "tvl_change": tvl_diff,
    }
