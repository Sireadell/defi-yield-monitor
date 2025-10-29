from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
from src.models.base import Base


class DepositModel(Base):
    __tablename__ = "deposits"

    id = Column(String, primary_key=True)
    pool_id = Column(String, ForeignKey("pools.pool_id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
