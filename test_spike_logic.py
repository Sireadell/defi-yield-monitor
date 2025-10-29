# src/test_spike_logic.py

from datetime import datetime, timedelta
from src.db.session import get_db
from src.db.models import PoolModel
from src.data.detector import detect_spikes

def run_spike_test():
    with get_db() as db:
        # Clean any previous test pool (repeatable)
        db.query(PoolModel).filter(PoolModel.name=="TestPool").delete()
        db.commit()

        # Insert baseline record
        db.add(PoolModel(
            name="TestPool",
            tvl=1000,      # initial TVL
            apr=5,         # initial APR
            created_at=datetime.utcnow()
        ))
        db.commit()

        # Insert record simulating a spike
        db.add(PoolModel(
            name="TestPool",
            tvl=1500,      # +50% TVL spike
            apr=10,        # +100% APR spike
            created_at=datetime.utcnow() + timedelta(hours=1)
        ))
        db.commit()

        # Run the spike detector
        spikes = detect_spikes(db, lookback_hours=2)
        if spikes:
            print("✅ Spike detected:")
            for s in spikes:
                print(s)
        else:
            print("❌ No spikes detected — something is wrong.")

        # Clean up test records
        db.query(PoolModel).filter(PoolModel.name=="TestPool").delete()
        db.commit()

if __name__ == "__main__":
    run_spike_test()
