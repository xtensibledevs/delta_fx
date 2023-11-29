import os
from celery import Celery
import docker
import requests
import tempfile
from git import Repo
from flask import session

from app import celery

def get_user_repos(username):
    headers = {'Authorization': f'Bearer {session["github_token"][0]}'}
    response = requests.get(f'https://api.github.com/users/{username}/repos', headers=headers)
    return response.json()


@celery.task(name='container_manager.build_docker_image')
def build_docker_image(image_name, context_path):
    # Build the Docker image for deployment
    client = docker.from_env()
    image, logs = client.images.build(path=context_path, tag=image_name)
    for log in logs:
        print(log)
    return image


# if __name__ == "__main__":
#     repo_url = "https://api.github.com/repos/r3tr056/legal-assitr-ai-engine.git"
#     destination = "docker_project"
#     image_name = 'python-flask-docker'
#     oauth2_token = "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"

#     if clone_repo(repo_url=repo_url, oauth2_token=oauth2_token, private=False):
#         print(f"Repo cloned to {destination}")
#     else:
#         print(f"Failed to clone repo")
    