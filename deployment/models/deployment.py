from datetime import datetime
import json
import uuid

class Deployment:
    def __init__(self, deployment_id, deployment_name, deployment_details, deployment_rev, project_id, user_id, deleted=False, is_running=True) -> None:
        self.deployment_id = uuid.uuid4().hex if not deployment_id else deployment_id
        self.deployment_name = deployment_name
        self.project_id = project_id
        self.user_id = user_id
        # the deployment revision, version data
        self.deployment_details = deployment_details
        self.deployment_rev = deployment_rev
        self.date_created = datetime.utcnow()
        self.deployment_date = datetime.utcnow()
        self.deleted = deleted
        self.is_running = is_running

    def dict(self):
        return {
            "id": self.deployment_id,
            "name": self.deployment_name,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "deployment_details": self.deployment_details,
            "deployment_rev": json.dumps(self.deployment_rev),
            "date_created": self.date_created,
            "deleted": self.deleted,
            "is_running": self.is_running,
        }
    
    def is_deleted(self):
        return self.deleted
