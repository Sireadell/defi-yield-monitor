from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from src.models.base import Base

class PoolModel(Base):
    __tablename__ = "pools"
    __table_args__ = {'extend_existing': True}  # redefinition conflict

    pool_id = Column(String, primary_key=True)
    protocol = Column(String, nullable=False)
    chain = Column(String, nullable=False)
    apy = Column(Float, nullable=False)
    tvl = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
