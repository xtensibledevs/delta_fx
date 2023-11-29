
from flask import Blueprint, request, current_app, jsonify
from flask_login import login_required, current_user
from flask_socketio import emit
from app import socketio
from deployment.models.project import Project

from deployment_service.project_manager.manage_projects import delete_project_task, provision_project

projects_router = Blueprint(__name__, url_prefix='projects')

@projects_router.route('/', methods=['GET'])
@login_required
def get_all_projects():
    if request.method == 'GET':
        db = current_app.extensions.get('MONGODB')
        projects = []
        projects_data = db.projects.find({'user_id': current_user.id})
        if not projects_data:
            return jsonify({'error': f'No projects under the user found'}), 404
        
        for project_data in projects_data:
            projects.append(project_data)
        
        return jsonify(projects), 200
    
    return jsonify({'error': 'Bad request'}), 400

# TODO : based on the front-end forms, the WS api will be designed
@socketio.on('create', namespace='dashboard/project')
def create_project():
    db = current_app.extensions.get('MONGODB')
    user_id = current_user.id
    project_id = request.json.get('project_id')
    project_name = request.json.get('project_name')
    
    try:
        project = Project(project_id, project_name, user_id)
        project_data = project.dict()
        result = provision_project.apply_async(args=[project_id, user_id])
        db.projects.insert_one(project_data)
        emit('status', {'msg': 'Project created', 'data': project_data})
    except Exception as ex:
        emit('status', {'msg': f"Unable to create project. Error : {ex}"})


@projects_router.route('/<project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    db = current_app.extensions.get('MONGODB')
    if request.method == 'GET':
        user_id = current_user.id
        project_data = db.projects.find_one({'project_id': project_id, 'user_id': user_id})
        if project_data is None:
            jsonify({'error': f'Project with project id {project_id} not found'}), 404

        return jsonify({'project': project_data}), 200
    
    return jsonify({'error': 'Bad request'}), 400

@projects_router.route('/<project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    db = current_app.extensions.get('MONGODB')
    if request.method == 'DELETE':
        user_id = current_user.id
        try:
            project_exists = db.projects.find_one({'project_id': project_id, 'user_id': user_id})
            if project_exists:
                result = delete_project_task.apply_async(args=[project_id, user_id])
                return jsonify({'message': f'Project with project id : {project_id} started deletion'}), 202
            return jsonify({'message': f'Project with project id : {project_id} not found'}), 404
        except Exception as ex:
            return jsonify({'error': f'Internal Server Error occured : {ex}'}), 500
        
    return jsonify({'error': 'Bad request'}), 400
        

@projects_router.route('/<project_id>/retire', methods=['GET'])
@login_required
def retire_project(project_id):
    db = current_app.extensions.get('MONGODB')
    if request.method == 'GET':
        user_id = current_user.id
        try:
            project_exists = db.projects.find_one({'project_id': project_id, 'user_id': user_id})
            if project_exists:
                result = retire_project_task.apply_async(args=[project_id, user_id])
                return jsonify({'message': f'Project with project id : {project_id} scheduled for returement'}), 202
            return jsonify({'message': f'Project with project id : {project_id} not found'}), 404
        except Exception as ex:
            return jsonify({'error': f'Internal server error occured : {ex}'}), 500
        
    return jsonify({'error': 'Bad request'}), 400
