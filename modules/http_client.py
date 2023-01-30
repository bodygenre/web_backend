import aiohttp
import asyncio
import json

async def get(url, **kwargs):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), **kwargs) as session:
        async with session.get(url) as resp:
            return await resp.read()

async def getJson(url, **kwargs):
    return json.loads(await get(url, *kwargs))

def register(*args, **kwargs):
    pass

