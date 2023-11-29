import os

from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask_socketio import emit
from app import mongo, app, socketio
from deployment_service.docker_deploy.docker_deploy import deploy_docker_container, get_deployment_status, list_docker_containers, stop_docker_container
from deployment.models.deployment import Deployment

blueprint = Blueprint('auth', __name__)


@blueprint.route('/deploy', methods=['POST'])
@login_required
def deploy():
    data = request.get_json()

    project_id = data.get('project_id')
    deployment_name = data.get('deployment_name')
    deployment_rev = data.get('deployment_rev')
    deployment_details = data.get('deployment')
    # deployment details from the json request
    image_name = deployment_details.get('image_name')
    service_name = deployment_details.get('service_name')
    replicas = deployment_details.get('replicas')
    ports_mapping = deployment_details.get('ports_mapping')
    environ = deployment_details.get('environ')

    if not project_id:
        return jsonify({'error':'Missing project_id'}), 400
    
    project = mongo.db.projects.find_one({'id': project_id, 'user_id': current_user.id})
    if not project:
        return jsonify({'error': f'Project with project_id: {project_id} not found'}), 404
    
    service_id = deploy_docker_container(image_name, service_name, replicas, ports_mapping, environ, user_id=current_user.id)

    deployment = Deployment(
        deployment_id=service_id,
        deployment_name=deployment_name,
        deployment_rev=deployment_rev,
        deployment_details=deployment_details,
        project_id=project['id'],
        user_id=current_user.id
    )
    mongo.db.deployments.insert_one(deployment.dict())
    
    return jsonify({
        'deployment_id': deployment.deployment_id,
        'message': 'Deployment succesfully created'
    }), 201

@blueprint.route('/deployment/halt/<deployment_id>', methods=['GET'])
@login_required
def halt_deployment(deployment_id):
    deployment = mongo.db.deployments.find_one({'deployment_id': deployment_id, 'user_id': current_user.id})
    if not deployment:
        return jsonify({'error': f'Deployment with id {deployment_id} not found'}), 404
    
    if deployment.is_running:
        try:
            socketio.emit('status_update', {
                'deployment_id': deployment_id,
                'status':'Deployment halt started'
            }, namespace='deployments/halt_deployment')
            task = stop_docker_container.apply_async(args=[deployment_id])
            return task.result
        

            return jsonify({"task_id": task.id}), 202
        
            result = mongo.db.deployments.update_one({'deployment_id': deployment_id, 'user_id': current_user.id}, {'$set': {'is_running': False}})
            if result.modified_count == 1:
                return jsonify({'message': f'Deployment with ID {deployment_id} successfully halted'}), 200
            else:
                return jsonify({'error': f'Unable to update status of deployment'}), 500
        except Exception as ex:
            return jsonify({'error': str(ex)}), 500
        
    return jsonify({'message': f'Deployment with ID {deployment_id} is already halted'})


@blueprint.route('/deployments', methods=['GET'])
@login_required
def get_deployments():
    user = mongo.db.users.find_one({'_id': current_user.id})
    if not user:
        return jsonify({'error': f'User with ID {current_user.id} not found'}), 404
    
    projects = mongo.db.projects.find({'user_id': current_user.id})
    deployments = {}

    for project in projects:
        deployments = mongo.db.deployments.find({'project_id': project['_id'], 'user_id': current_user.id})
        deployments[project] = deployments

    return jsonify({'deployments': deployments}), 200


@blueprint.route('/deployments/status/<deployment_id>', methods=['GET'])
@login_required
def get_deployment_status(deployment_id):
    deployment = mongo.db.deployments.find_one({'deployment_id': deployment_id, 'user_id': current_user.id})
    if not deployment:
        return jsonify({'error': f'Deployment with id {deployment_id} not found'}), 404

    deployment_status = get_deployment_status(deployment_id)
    return jsonify({
        'id': deployment_id,
        'name': deployment.name,
        'status': deployment_status
    }), 200


UPLOAD_FOLDER = '/dockerfiles'

@blueprint.route('/deployments/deploy/dockerfile', methods=['POST'])
@login_required
def deploy_dockerfile():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    docker_file = request.files.get('dockerfile')
    if docker_file.filename == '':
        return jsonify({'error': 'No selected file'})
    if docker_file:
        filename = secure_filename(docker_file.filename)
        docker_file.save(os.path.join(os.getcwd(), UPLOAD_FOLDER, filename))
        return jsonify({'message': 'success'})
