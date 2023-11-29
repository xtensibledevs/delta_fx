import yaml
from config import celery


def generate_service_compose(service_name, image, ports, environ=None, **other_config):
    service_compose = {
        'version': '3.8',
        'services': {
            service_name: {
                'image': image,
                'ports': ports,
            }
        }
    }

    # if the environment is provided
    if environ:
        service_compose['services'][service_name]['environment'] = environ

    # apply other config
    if other_config:
            service_compose['services'][service_name].update(other_config)

    return service_compose


def generate_docker_compose(service_name, image, ports):
    docker_compose = {
        'version': '3.8',
        'services': {
            service_name: {
                'image': image,
                'ports': ports,
            }
        }
    }

    return docker_compose

def generate_appkit_compose(project_name):
    docker_compose = {
        'version': '3.8',
        'services': {
            'auth-service': {
                'image': f"{project_name}_auth",
            },
            'push-notify-service': {
                'image': f"{project_name}_push_notify",
            },
            'blob-store': {
                'image': f"{project_name}_blob_store",

            },
            'postgres': {
                'deploy': {
                    'resources': {
                        'limits': {
                            'cpu': "${DOCKER_POSTGRES}"
                        }
                    }
                }
            }
        }
    }


def setup_backend():
    docker_compose = {
        'version': '3.8',
        'services': {
            'backend': {
                'restart': 'always',
                'build': {
                    'context': 'backend',
                    'target': 'development',
                },
                'volumes': [
                    './backend:/usr/src/app',
                    '/usr/src/app/node_modules'
                ],
                'depends_on': [
                    'database'
                ],
                'networks': [
                    'express-mongo',
                    'react-express'
                ],
                'expose': ['3000'],

            }
        }
    }

    return docker_compose


def generate_database_compose(database_service_name, image, ports, environment):
    database_compose = {
        'version': '3.8',
        'services': {
            database_service_name: {
                'image': image,
                'ports': ports,
                'environment': environment,
            }
        }
    }

    return database_compose

def write_docker_compose(docker_compose, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(docker_compose, file, default_flow_style=False)

