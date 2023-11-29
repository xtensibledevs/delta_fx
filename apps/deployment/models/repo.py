import os
from git import Repo

class GitRepository:
    def __init__(self, platform, owner, repo_name, branch_to_deploy, webhook_urls, local_path=None):
        self.platform = platform
        self.owner = owner
        self.repo_name = repo_name
        self.local_path = local_path
        self.deployment_branch = branch_to_deploy
        self.webhook_urls = webhook_urls
        self.url = self.generate_repo_url()

    def generate_repo_url(self):
        if self.platform.lower() == 'github':
            return f'https://github.com/{self.owner}/{self.repo_name}.git'
        elif self.platform.lower() == 'bitbucket':
            return f'https://bitbucket.org/{self.owner}/{self.repo_name}.git'
        elif self.platform.lower() == 'gitlab':
            return f'https://gitlab.com/{self.owner}/{self.repo_name}.git'
        else:
            raise ValueError(f"Unsupported platform: {self.platform}")
        
    @property
    def is_cloned(self):
        return os.path.exists(os.path.join(self.local_path, self.repo_name))
    
    def get_repo_details(self):
        if self.is_cloned:
            repo = Repo(os.path.join(self.local_path, self.repo_name))
            # git commit history
            commit_history = [{'hash': commit.hexsha, 'message': commit.message} for commit in repo.iter_commits()]
            # latest commit
            latest_commit = {'hash': repo.head.commit.hexsha, 'message': repo.head.commit.message}
            # the current branch name
            current_branch = repo.active_branch.name

            return {
                'commit_history': commit_history,
                'latest_commit': latest_commit,
                'current_branch': current_branch
            }
    
