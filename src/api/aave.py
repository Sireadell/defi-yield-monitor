import aiohttp
import asyncio
from datetime import datetime
from decimal import Decimal
from src.models.pool import Pool

# Multi-chain Aave V3 subgraph endpoints
CHAIN_SUBGRAPHS = {
    "Ethereum": "https://api.thegraph.com/subgraphs/name/aave/protocol-v3",
    "Polygon": "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-polygon",
    "Arbitrum": "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-arbitrum",
    "Optimism": "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-optimism",
}

class AaveClient:
    def __init__(self, chain: str = "Ethereum"):
        self.base_url = CHAIN_SUBGRAPHS.get(chain, CHAIN_SUBGRAPHS["Ethereum"])
        self.session = None

    async def _get(self, query: str, variables: dict = None):
        if not self.session:
            self.session = aiohttp.ClientSession()
        payload = {"query": query, "variables": variables or {}}
        for _ in range(3):  # Retry 3 times
            try:
                async with self.session.post(self.base_url, json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except Exception:
                await asyncio.sleep(1)
        return {}

    async def fetch_pools(self):
        """
        Fetch all Aave pools (reserves) for this client chain.
        Returns a list of Pool objects with accurate APY in percent.
        """
        query = """
        query {
            reserves(first: 50) {
                id
                symbol
                name
                liquidityRate
                totalLiquidity
            }
        }
        """
        data = await self._get(query)
        pools = []
        for item in data.get("data", {}).get("reserves", []):
            # Correct RAY (10^27) to APY %
            liquidity_rate_ray = Decimal(item.get("liquidityRate", 0))
            apy_percent = float(liquidity_rate_ray / Decimal(10**27) * 100)

            pools.append(
                Pool(
                    pool_id=item["id"],
                    protocol="Aave",
                    chain=[k for k, v in CHAIN_SUBGRAPHS.items() if v == self.base_url][0],
                    apy=apy_percent,
                    tvl=float(Decimal(item.get("totalLiquidity", 0))),
                    last_updated=datetime.utcnow()
                )
            )
        return pools

    async def fetch_deposits(self, pool_id: str):
        """
        Fetch total deposits (supply) for a specific pool.
        Returns float (totalLiquidity).
        """
        query = """
        query($poolId: ID!) {
            reserves(where: {id: $poolId}) {
                totalLiquidity
            }
        }
        """
        variables = {"poolId": pool_id}
        data = await self._get(query, variables)
        reserves = data.get("data", {}).get("reserves", [])
        if reserves:
            return float(Decimal(reserves[0].get("totalLiquidity", 0)))
        return 0.0

    async def close(self):
        if self.session:
            await self.session.close()
