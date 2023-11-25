
from typing import Any


class Project:
    def __call__(self, project_name, user_id) -> Any:
        self.project_name = project_name
        self.user_id = user_id