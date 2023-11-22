
import docker

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

def list_docker_containers():
    client = docker.from_env()
    containers = client.containers.list()
    return containers

def stop_docker_container(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.stop()
    print(f"Container {container_name} stopped.")


def remove_docker_container(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.remove()
    print(f"Container {container_name} removed.")

def start_docker_container(container_name):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.start()
    print(f"Container {container_name} started.")
