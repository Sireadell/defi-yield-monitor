# src/test_spike_logic.py

from datetime import datetime, timedelta
from src.db.session import get_db
from src.db.models import PoolModel

# Spike thresholds (percent change)
TVL_THRESHOLD = 20    # detect if TVL changes by 20% or more
APR_THRESHOLD = 50    # detect if APR changes by 50% or more

def run_spike_test():
    with get_db() as db:
        # Clean any previous test pool
        db.query(PoolModel).filter(PoolModel.pool_id=="TestPool").delete()
        db.commit()

        # Step 1: Insert baseline record
        db.add(PoolModel(
            pool_id="TestPool",
            tvl=1000,           # initial TVL
            apy=5,              # initial APR
            last_updated=datetime.utcnow(),
            protocol="TestProtocol",
            chain="TestChain"
        ))
        db.commit()

        # Step 2: Insert record simulating a spike
        db.add(PoolModel(
            pool_id="TestPool",
            tvl=1500,           # +50% TVL spike
            apy=10,             # +100% APR spike
            last_updated=datetime.utcnow() + timedelta(hours=1),
            protocol="TestProtocol",
            chain="TestChain"
        ))
        db.commit()

        # Step 3: Fetch last two records for TestPool
        records = db.query(PoolModel).filter(PoolModel.pool_id=="TestPool").order_by(PoolModel.last_updated).all()
        if len(records) < 2:
            print("Not enough records to test spike.")
            return

        prev, curr = records[-2], records[-1]

        # Step 4: Calculate changes
        tvl_change = ((curr.tvl - prev.tvl) / prev.tvl) * 100
        apr_change = ((curr.apy - prev.apy) / prev.apy) * 100

        # Step 5: Check for spikes
        spikes = []
        if abs(tvl_change) >= TVL_THRESHOLD or abs(apr_change) >= APR_THRESHOLD:
            spikes.append({
                "pool_id": curr.pool_id,
                "tvl_change": round(tvl_change, 2),
                "apr_change": round(apr_change, 2)
            })

        # Step 6: Print results
        if spikes:
            print("✅ Spike detected:")
            for s in spikes:
                print(s)
        else:
            print("❌ No spikes detected — check thresholds or data.")

        # Step 7: Clean up test records
        db.query(PoolModel).filter(PoolModel.pool_id=="TestPool").delete()
        db.commit()

if __name__ == "__main__":
    run_spike_test()
