from functools import wraps

from flask import current_app, jsonify, request, session
from flask_login import login_required, current_user
import jwt

from apps.auth.models.user import User
from deployment.models.deployment import Deployment

def jwt_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        current_user = None
        db = current_app.extensions.get('MONGODB')

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({'error': 'Auth token is missing'})
        
        try:
            data = jwt.decode(token, current_app.secret_key, algorithms='HS256')
            user_data = db.users.find_one({'email': data['email']})
            current_user = User.make_from_dict(user_data) if user_data else None
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        if current_user is None:
            return jsonify({'error': 'User not found'}), 404
        
        return f(current_user, db, *args, **kwargs)
    return decorated

@login_required
def get_deployment_by_id(deployment_id):
    db = current_app.extensions.get('MONGODB')
    deployment_data = db.deployments.find_one({'id': deployment_id})
    if deployment_data is not None:
        return Deployment.make_from_dict(deployment_data)
    return None

@login_required
def get_github_token():
    github_token = current_user.github_token
    return github_token

def use_deployment_creds(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        deployment_id = request.json.get('deployment_id')
        if deployment_id is None:
            return jsonify({'error': 'Deployment id is missing'})
        
        deployment = get_deployment_by_id(deployment_id)
        if deployment is None:
            return jsonify({'error': f'No deployment with deployment id : {deployment_id} exists'}), 404
        
        repo_owner = deployment.github_owner
        repo_name = deployment.github_repo_name
        github_token = get_github_token(deployment.user_id)
        if github_token is None:
            return jsonify({'error': 'No github oauth token found'})
        
        return func(repo_owner=repo_owner, repo_name=repo_name, token=github_token)
    
    return decorated