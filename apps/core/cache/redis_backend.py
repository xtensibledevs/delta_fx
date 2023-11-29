import os
import inspect
import pickle
from typing import Any, Callable

from redis.asyncio import aioredis
import ujson

from core.cache.base_backend import BaseBackend

REDIS_URL = os.environ.get('REDIS_URL')

redis = aioredis.from_url(url=REDIS_URL)

def make_key(function: Callable, prefix):
    path = f"{prefix}::{inspect.getmodule(function).__name__}.{function.__name__}"
    args = ""

    for arg in inspect.signature(function).parameters.values():
        args += arg.name

    if args:
        return f"{path}.{args}"
    
    return path

class RedisBackend(BaseBackend):
    async def get(self, key:str):
        result = await redis.get(key)
        if not result:
            return
        try:
            return ujson.loads(result.decode('utf-8'))
        except UnicodeDecodeError:
            return pickle.loads(result)
        
    async def set(self, response, key, ttl=60):
        if isinstance(response, dict):
            response = ujson.dumps(response)
        elif isinstance(response, object):
            response = pickle.dumps(response)

        await redis.set(name=key, value=response, ex=ttl)

    async def delete_startswith(self, value):
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)

