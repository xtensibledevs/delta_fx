
import docker
import subprocess

from config import celery


@celery.task(bind=True)
def deploy_docker_container(image_name, service_name, replicas, ports_mapping, environ):
    # create a docker client
    client = docker.from_env()

    service_options = {
        'image': image_name,
        'name' : service_name,
        'replicas': replicas,
        'ports' : ports_mapping,
    }

    # Add env variables if provided
    if environ:
        service_options['environment'] = environ

    service = client.services.create(**service_options)
    
    print(f"Service {service_name} deployed with ID {service.id}")
    return service.id


@celery.task
def list_docker_containers():
    client = docker.from_env()
    containers = client.containers.list()
    return containers
    

@celery.task
def stop_docker_container(deployment_id):
    client = docker.from_env()
    try:
        container = client.containers.get(deployment_id)
        container.stop()
    except docker.errors.APIError as e:
        status = f"Failed to halt deployment {deployment_id}. Error {e}"
    return status
    

@celery.task
def remove_docker_container(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.remove()
    print(f"Container {container_name} removed.")

@celery.task
def start_docker_container(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.start()
    print(f"Container {container_name} started.")

@celery.task
def get_deployment_status(deployment_id):
    try:
        client = docker.from_env()
        container = client.containers.get(deployment_id)
        status = container.status
        return status
    except docker.errors.NotFound:
        return f"Container with name `{deployment_id}` not found."
    except docker.errors.APIError as e:
        return f'Error while getting container status : {e}'
    
@celery.task
def offload_container(container_id, image_name, image_version, tarball_file):
    client = docker.from_env()
    # commit the running container
    new_image = client.containers.get(container_id).commit(repository=image_name, tags=image_version)
    # save the new image to a tarball
    with open(tarball_file, 'wb') as tarball:
        for chunk in new_image.save():
            tarball.write(chunk)

    # remove the original container
    client.containers.get(container_id).remove(force=True)

@celery.task
def load_container(image_name, image_version, tarball_file):
    client = docker.from_env()
    # load the image from the tarball
    with open(tarball_file, 'rb') as tarball:
        client.images.load(data=tarball.read())

    # Run a new container from the loaded image
    client.containers.run(f"{image_name}:{image_version}", detach=True)
