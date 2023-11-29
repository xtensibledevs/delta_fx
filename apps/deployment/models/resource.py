
from dataclasses import dataclass

@dataclass
class Resource:
    def __init__(self, name, owner, access_policy_id):
        self.name = name
        self.owner = owner
        self.access_policy_id = access_policy_id

    @classmethod
    def make_from_dict(cls, d):
        return cls(d['name'], d['owner'])
    
    def dict(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "access_policy_id": self.access_policy_id,
        }
    