# src/test_full_spike_run.py

from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import SQLAlchemyError
from src.db.database import engine
from src.db.models import Base, PoolModel
from src.db.session import get_db

# Spike thresholds
TVL_THRESHOLD = 20    # percent
APR_THRESHOLD = 50    # percent

def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created or already exist.")
    except SQLAlchemyError as e:
        print("❌ Failed to create tables:", e)

def run_spike_test():
    errors = []

    try:
        with get_db() as db:
            # Clean any previous test pool
            try:
                db.query(PoolModel).filter(PoolModel.pool_id == "TestPool").delete()
                db.commit()
            except Exception as e:
                db.rollback()
                errors.append(f"Error cleaning test pool: {e}")

            # Insert baseline record
            try:
                baseline = PoolModel(
                    pool_id=f"TestPool_{datetime.now().timestamp()}_base",
                    tvl=1000,
                    apy=5,
                    last_updated=datetime.now(timezone.utc),
                    protocol="TestProtocol",
                    chain="TestChain"
                )
                db.add(baseline)
                db.commit()
            except Exception as e:
                db.rollback()
                errors.append(f"Error inserting baseline: {e}")

            # Insert spike record (new row, slightly later timestamp)
            try:
                spike = PoolModel(
                    pool_id=f"TestPool_{datetime.now().timestamp()}_spike",
                    tvl=1500,
                    apy=10,
                    last_updated=datetime.now(timezone.utc) + timedelta(hours=1),
                    protocol="TestProtocol",
                    chain="TestChain"
                )
                db.add(spike)
                db.commit()
            except Exception as e:
                db.rollback()
                errors.append(f"Error inserting spike: {e}")

            # Fetch last two records for comparison (use protocol/chain filter)
            try:
                records = (
                    db.query(PoolModel)
                    .filter(PoolModel.protocol == "TestProtocol", PoolModel.chain == "TestChain")
                    .order_by(PoolModel.last_updated)
                    .all()
                )

                if len(records) < 2:
                    errors.append("Not enough records to test spike.")
                else:
                    prev, curr = records[-2], records[-1]
                    tvl_change = ((curr.tvl - prev.tvl) / prev.tvl) * 100
                    apr_change = ((curr.apy - prev.apy) / prev.apy) * 100

                    if tvl_change >= TVL_THRESHOLD or apr_change >= APR_THRESHOLD:
                        print("✅ Spike detected:")
                        print({
                            "pool_id_prev": prev.pool_id,
                            "pool_id_curr": curr.pool_id,
                            "tvl_change": round(tvl_change, 2),
                            "apr_change": round(apr_change, 2)
                        })
                    else:
                        print("❌ No spike detected, check thresholds or data.")
            except Exception as e:
                errors.append(f"Error fetching/comparing records: {e}")

            # Clean up test records
            try:
                db.query(PoolModel).filter(
                    PoolModel.protocol == "TestProtocol", PoolModel.chain == "TestChain"
                ).delete()
                db.commit()
            except Exception as e:
                db.rollback()
                errors.append(f"Error cleaning up: {e}")

    except Exception as e:
        errors.append(f"DB session error: {e}")

    if errors:
        print("\n⚠️ Errors found during test run:")
        for err in errors:
            print("-", err)

if __name__ == "__main__":
    create_tables()
    run_spike_test()
