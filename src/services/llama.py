import aiohttp

# Fetch yield data from DefiLlama API
async def fetch_yields():
    url = "https://yields.llama.fi/pools"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            pools = data.get("data", [])
            # Keeping only a few for testing
            return pools[:5]
