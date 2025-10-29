import aiohttp
from datetime import datetime

class AaveFetcher:
    API_URL = "https://aave-api-v2.aave.com/data/pools"

    async def fetch(self):
        """Fetch live Aave pool data and normalize it for DB storage."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch data. Status: {response.status}")
                data = await response.json()

        # Normalize to match your PoolModel
        formatted = []
        for item in data:
            formatted.append({
                "pool_id": item.get("id"),
                "protocol": "Aave",
                "chain": item.get("network", "unknown"),
                "apy": float(item.get("supplyAPY", 0)) * 100,
                "tvl": float(item.get("totalLiquidityUSD", 0)),
                "last_updated": datetime.utcnow()
            })

        return formatted
