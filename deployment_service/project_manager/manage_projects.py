
from app import celery

@celery.task(bind=True, acks_late=True, name='project_manager.delete_project')
def delete_project_task():
    # filter_criteria = {"project_id": project_id, "user_id": user_id}
    # update_data = {"$set": {"deleted": True}}
    pass

@celery.task(bind=True, acks_late=True, name='project_manager.provision_project')
def provision_project():
    pass

@celery.task(bind=True)
def retire_project_task():
    pass