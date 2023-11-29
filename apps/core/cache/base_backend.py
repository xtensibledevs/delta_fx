from abc import ABC, abstractmethod
from typing import Any

class BaseBackend(ABC):
    @abstractmethod
    async def get(self, key):
        ...

    @abstractmethod
    async def set(self, response, key, ttl=60):
        ...

    @abstractmethod
    async def delete_startswith(self, value):
        ...