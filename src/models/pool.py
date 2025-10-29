
# src/models/pool.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict  

class Pool(BaseModel):
    pool: str  # unique pool identifier, required by DefiLlama data
    chain: str
    project: str
    symbol: str
    tvlUsd: float
    apyBase: Optional[float] = None
    apyReward: Optional[float] = None
    apy: Optional[float] = None
    rewardTokens: Optional[List[str]] = None
    pool: str
    apyPct1D: Optional[float] = None
    apyPct7D: Optional[float] = None
    apyPct30D: Optional[float] = None
    stablecoin: Optional[bool] = False
    ilRisk: Optional[str] = None
    exposure: Optional[str] = None
    predictions: Optional[dict] = None
    poolMeta: Optional[str] = None
    mu: Optional[float] = None
    sigma: Optional[float] = None
    count: Optional[int] = None
    outlier: Optional[bool] = None
    underlyingTokens: Optional[List[str]] = None
    il7d: Optional[float] = None
    apyBase7d: Optional[float] = None
    apyMean30d: Optional[float] = None
    volumeUsd1d: Optional[float] = None
    volumeUsd7d: Optional[float] = None
    apyBaseInception: Optional[float] = None
