from config import celery, docker_client

@celery.task
def deploy_docker_stack(stack_id, compose_file, environ=None):
    stack_options = {
        'compose_file': compose_file,
        'stack_id': stack_id,
    }

    if environ:
        stack_options['environment'] = environ

    stack = docker_client.stacks.deploy(**stack_options)

    if stack:
        print(f"Stack {stack_id} deployed.")
    return stack_id


@celery.task
def scale_docker_service(service_name, replicas):
    service = docker_client.services.get(service_name)
    service.scale(replicas)
    print(f"Service {service_name} scaled to {replicas} replicas.")

@celery.task
def remove_docker_stack(stack_id):
    stack = docker_client.stacks.get(stack_id)
    stack.remove()
    print(f"Stack {stack_id} removed.")
