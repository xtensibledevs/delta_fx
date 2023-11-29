import functools
from dataclasses import dataclass

@dataclass(frozen=True)
class Principal:
    key: str
    value: str

    def __repr__(self):
        return f"{self.key}:{self.value}"
    
    def __str__(self):
        return self.__repr__()

@dataclass(frozen=True)    
class SystemPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs):
        super().__init__(key="system", value=value, *args, **kwargs)

@dataclass(frozen=True)
class UserPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs):
        super().__init__(key="user", value=value, *args, **kwargs)

@dataclass(frozen=True)
class RolePrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs):
        super().__init__(key="role", value=value, *args, **kwargs)

