import requests
import json
import os
import errno
import secrets
import string
from flask import Blueprint, request
from celery.exceptions import Reject

from app import celery

deploy_hook = Blueprint(__name__)

@celery.task(bind=True, acks_late=True)
def create_commit_webhook(self, repo_owner, repo_name, token, branches):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/hooks'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    webhook_url = generate_webhook_uurl()
    payload = {
        'name': 'web',
        'active': True,
        'events': ['push'],
        'config': {
            'url': webhook_url,
            'content-type': 'json',
        },
        'branches': branches,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 201:
            print(f'Webhook added successfully! ID : {response.json().get("id")}')
    except requests.exceptions.RequestException as ex:
        raise Reject(ex, requeue=False)
    except Exception as ex:
        raise self.retry(ex, countdown=10)
        
def generate_webhook_uurl():
    characters = string.ascii_letters + string.digits + '-_'
    random_string = ''.join(secrets.choice(characters) for _ in range(64))
    host_domain = os.environ.get('HOST_DOMAIN')
    webhook_ep = f"{host_domain}/deployments/hooks/{random_string}"
    return webhook_ep
    
@celery.task(bind=True, acks_late=True)
def get_gh_deployments(self, repo_owner, repo_name, token, sha_creation=None, task=None, environment=None):
    """
    Get the deployments of the Repo

    Args:
    - repo_owner : Repository owner username
    - repo_name : Repository name
    - token : Github OAuth token
    - sha_creation : `Filter` The SHA at the time of creation
    - task : `Filter` The task of the deployment
    - environment : `Filter` The environment of the deployment
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/deployments"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
    }
    payload = {
        'sha': sha_creation,
        'task': task,
        'environment': environment,
    }

    deployments = {}

    try:
        response = requests.get(url, headers=headers, json=payload)
        response = json.loads(response.json())
    except requests.exceptions.RequestException as ex:
        Reject(ex, requeue=False)
    except Exception as ex:
        self.retry(ex, countdown=10)

    # populate the deployments
    for dep in deployments:
        deployments[dep['id']] = {
            'ref': dep.get('ref'),
            'sha': dep.get('sha'),
            'task': dep.get('task'),
            'description': dep.get('description'),
            'original_environment': dep.get('original_environment'),
            'environment': dep.get('environment'),
            'transient_environment': dep.get('transient_environment'),
            'production_environment': dep.get('production_environment'),
            'created_at': dep.get('created_at'),
            'updated_at': dep.get('updated_at'),
            
        }

    return deployments
    
def create_gh_deployment(repo_owner, repo_name, ref, token, environment, description, transient_deploy=False, production_deploy=False):
    """
    Create a fresh deployment on github

    Args:
    - repo_owner : Repository owner username
    - repo_name : Repository name
    - ref : The Branch or Commit SHA
    - token : Github OAuth Token of user
    - environment : Name of the target deployment environment
    - description : Short description of the deployment
    - transient_deploy : Is the deployment transient ?
    - production_deploy : Is the deployment production ?

    Returns:
    - deployment_id : The deployment id of the created deployment
    """

    # endpoint to hit
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/deployments"
    # headers
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
    }
    # create deployment http payload
    payload = {
        'ref': ref,
        'task': 'deploy',
        'environment': environment,
        'description': description,
        'transient_environment': transient_deploy,
        'production_environment': production_deploy,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
    except Exception as e:
        return e
    return response.get("id")

def update_deployment_status(repo_owner, repo_name, deployment_id, state, target_url, log_url=None, description=None, environment=None, token=None, isProduction=False):
    """
    Update the deployment status on Github
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/deployments/{deployment_id}/statuses"

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    # status update payload
    payload = {
        'state': state,
        'target_url': target_url,
        "log_url": log_url,
        'description': description,
        'environment': environment,
        'production_environment': str(isProduction),
    }

    response = request.post(url, headers=headers, json=payload)

    return response

def delete_gh_deployment(repo_owner, repo_name, token, deployment_id):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/deployments/{deployment_id}'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json',
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        return True
    else:
        return False