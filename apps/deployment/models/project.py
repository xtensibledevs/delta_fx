from uuid import uuid4
from typing import Any


class Project:
    def __call__(self, project_id, project_name, user_id, deleted) -> Any:
        self.project_name = project_name
        self.user_id = user_id
        self.project_id = uuid4().hex if not project_id else project_id
        self.deleted = deleted

    @classmethod
    def make_from_dict(cls, d):
        return cls(
            d['project_id'],
            d['project_name'],
            d['user_id'],
            d['deleted']
        )
    
    def dict(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'user_id': self.user_id,
            'deleted': self.deleted,
        }