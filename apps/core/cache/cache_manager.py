
from functools import wraps

class CacheManager:
    def __init__(self, backend, key_maker):
        self.backend = backend
        self.key_maker = key_maker

    def cached(self, prefix, tag, ttl=60):
        def _cached(fx):
            @wraps(fx)
            async def __cached(*args, **kwargs):
                if not self.backend or not self.key_maker:
                    raise ValueError("Backend or KeyMaker not initialized")
                
                key = await self.key_maker.make(
                    function=function,
                    prefix=prefix if prefix else tag,
                )

                cached_response = await self.backend.get(key=key)
                if cached_response:
                    return cached_response
                
                response = await function(*args, **kwargs)
                await self.backend.set(response=response, key=key, ttl=ttl)
                return response
            
            return __cached
        
        return _cached
    
    async def remove_by_tag(self, tag):
        await self.backend.delete_startswith(value=tag)

    async def remove_by_prefix(self, prefix):
        await self.backend.delete_startswith(value=prefix)

Cache = CacheManager()