from sqlalchemy.orm import Session
from src.models.pool_model import PoolModel

def save_pool(db: Session, pool: PoolModel):
    existing = db.query(PoolModel).filter_by(pool_id=pool.pool_id).first()
    if existing:
        existing.apy = pool.apy
        existing.tvl = pool.tvl
        existing.last_updated = pool.last_updated
    else:
        db.add(pool)
    db.commit()
