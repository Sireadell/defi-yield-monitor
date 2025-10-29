from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
from src.db.base import Base

class PoolModel(Base):
    __tablename__ = "pools"
    pool_id = Column(String, primary_key=True)
    protocol = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    apy = Column(Float, nullable=False)
    tvl = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)

class DepositModel(Base):
    __tablename__ = "deposits"
    id = Column(String, primary_key=True)
    pool_id = Column(String, ForeignKey("pools.pool_id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
