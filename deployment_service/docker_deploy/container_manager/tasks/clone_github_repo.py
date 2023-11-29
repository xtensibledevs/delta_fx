import os
import tempfile
import requests
from git import Repo

from app import celery

@celery.task(name='container_manager.clone_github_repo')
def clone_github_repo(clone_url, oauth2_token, private=False):
    """
    Clone a github repo for deployment
    Args:
    - clone_url : The Clone URL of the repository
    - oauth2_token : Github OAuth Token for cloning private repositories
    - private : The repo is private or not
    Returns:
    - boolean : Wherether the task has completed or not
    """
    temp_dir = tempfile.gettempdir()

    # remove the git from the end of the url
    repo_info_url = f"{clone_url}.git"

    response = requests.get(repo_info_url, headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })

    if response.status_code != 200:
        print(f"Failed to get repository information. Status code {response.status_code}")
        return False

    destination_path = os.path.join(temp_dir, response.json()['name'])
    try:
        if private:
            Repo.clone_from(clone_url, destination_path, depth=1, progress=1, config=f"core.askPass=/bin/echo -e 'username={oauth2_token}\\npassword=x-oauth-basic'")
            return True
        else:
            Repo.clone_from(clone_url, destination_path)
            print(f"Cloned to {destination_path}")
            return True
    except Exception as e:
        return False