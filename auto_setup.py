# auto_setup.py
import os
from pathlib import Path

# Define project root (assuming this script runs from project root)
ROOT = Path.cwd()

# Ensure src exists
SRC = ROOT / "src"
SRC.mkdir(exist_ok=True)

# === 1. Create src/config.py ===
config_content = '''DATABASE_URL = "sqlite:///src/db/pools.db"

# Spike detection thresholds
SPIKE_APY_THRESHOLD = 0.25  # 25% change
SPIKE_TVL_THRESHOLD = 0.30  # 30% change
'''
(SRC / "config.py").write_text(config_content.strip() + "\n")

# === 2. Create src/db/base.py ===
db_base_content = '''from sqlalchemy.orm import declarative_base

Base = declarative_base()
'''
db_dir = SRC / "db"
db_dir.mkdir(exist_ok=True)
(db_dir / "base.py").write_text(db_base_content.strip() + "\n")

# === 3. Create src/db/models.py ===
db_models_content = '''from sqlalchemy import Column, String, Float, DateTime, ForeignKey
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
'''
(db_dir / "models.py").write_text(db_models_content.strip() + "\n")

# === 4. Create src/data/ + files ===
data_dir = SRC / "data"
data_dir.mkdir(exist_ok=True)

# fetcher.py
fetcher_content = '''import requests
from src.db.models import PoolModel
from datetime import datetime

def fetch_sample_pool():
    """Fetch one mock pool from DefiLlama API for test."""
    url = "https://yields.llama.fi/pools"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()["data"][0]
    return PoolModel(
        pool_id=data["pool"],
        protocol=data["project"],
        chain=data["chain"],
        apy=data.get("apy", 0.0),
        tvl=data.get("tvlUsd", 0.0),
        last_updated=datetime.utcnow(),
    )
'''
(data_dir / "fetcher.py").write_text(fetcher_content.strip() + "\n")

# detector.py
detector_content = '''from src.config import SPIKE_APY_THRESHOLD, SPIKE_TVL_THRESHOLD

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
'''
(data_dir / "detector.py").write_text(detector_content.strip() + "\n")

# __init__.py
(data_dir / "__init__.py").write_text("# package marker\n")

# === Done ===
print("All files created successfully!")
print("Created:")
print("  src/config.py")
print("  src/db/base.py")
print("  src/db/models.py")
print("  src/data/fetcher.py")
print("  src/data/detector.py")
print("  src/data/__init__.py")
print("\nRun your test now:")
print("python -m src.test_full_spike_detector")