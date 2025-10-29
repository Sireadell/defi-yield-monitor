from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src.db.models import PoolModel
from src.config import SPIKE_APY_THRESHOLD, SPIKE_TVL_THRESHOLD


def detect_spikes(db: Session, lookback_hours: int = 24):
    """
    Detect APY/TVL spikes in the last `lookback_hours` using DB history.
    Returns list of spike dicts.
    """
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)

    recent_pools = (
        db.query(PoolModel)
        .filter(PoolModel.last_updated >= cutoff)
        .order_by(PoolModel.pool_id, PoolModel.last_updated)
        .all()
    )

    spikes = []
    seen = set()

    for pool in recent_pools:
        key = (pool.pool_id, pool.last_updated)
        if key in seen:
            continue
        seen.add(key)

        prev = (
            db.query(PoolModel)
            .filter(
                PoolModel.pool_id == pool.pool_id,
                PoolModel.last_updated < pool.last_updated
            )
            .order_by(PoolModel.last_updated.desc())
            .first()
        )

        if not prev or prev.apy <= 0:
            continue

        apy_change = (pool.apy - prev.apy) / prev.apy
        tvl_change = (pool.tvl - prev.tvl) / prev.tvl if prev.tvl > 0 else 0

        if apy_change >= SPIKE_APY_THRESHOLD or tvl_change >= SPIKE_TVL_THRESHOLD:
            spikes.append({
                "pool_id": pool.pool_id,
                "protocol": pool.protocol,
                "chain": pool.chain,
                "apy_change_pct": round(apy_change * 100, 2),
                "tvl_change_pct": round(tvl_change * 100, 2),
                "from_apy": prev.apy,
                "to_apy": pool.apy,
                "from_tvl": prev.tvl,
                "to_tvl": pool.tvl,
                "detected_at": datetime.utcnow().isoformat()
            })

    return spikes, recent_pools  # ← Return both


def log_spikes(spikes, recent_pools=None):
    """Console logger: shows spikes OR current pool snapshot."""
    if not spikes:
        print("\nNo significant spikes detected.")
        if recent_pools:
            print("Current Pool Snapshot:")
            for p in recent_pools[-5:]:  # Show last 5 to avoid spam
                print(
                    f"→ {p.protocol.ljust(12)} | {p.chain.ljust(10)} | "
                    f"APY: {p.apy:6.2f}% | TVL: ${p.tvl:,.0f} | "
                    f"Pool: {p.pool_id[:10]}..."
                )
        return

    print(f"\n[ALERT] {len(spikes)} SPIKE(S) DETECTED:")
    for s in spikes:
        print(
            f"→ {s['protocol'].ljust(12)} | {s['chain'].ljust(10)} | "
            f"APY: {s['from_apy']:5.2f}% → {s['to_apy']:5.2f}% (+{s['apy_change_pct']:6.2f}%) | "
            f"TVL: ${s['from_tvl']:,.0f} → ${s['to_tvl']:,.0f} (+{s['tvl_change_pct']:5.1f}%) | "
            f"Pool: {s['pool_id'][:10]}..."
        )