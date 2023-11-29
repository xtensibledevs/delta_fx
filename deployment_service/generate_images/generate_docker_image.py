
import docker
from deployment_service.config import celery

@celery.task
def build_docker_image(image_name, path='.', dockerfile='Dockerfile', image_tag=None):
    client = docker.from_env()

    try:
        image, build_logs = client.images.build(
            path=path,
            dockerfile=dockerfile,
            tag=image_name if image_tag is None else image_tag,
            rm=True,
        )

        # Print Build logs
        for log in build_logs:
            print(log)

        print(f"Image {image_name} build successfully.")

    except docker.errors.BuildError as e:
        print(f"Failed to build image {image_name}. Error : {e}")
    except docker.errors.APIError as e:
        print(f"Docker API error while building image {image_name}. Error: {e}")

@celery.task
def pull_docker_image(image_name, tag='latest'):
    client = docker.from_env()

    try:
        client.images.pull(image_name, tag=tag)
        print(f"Image {image_name}:{tag} pulled successfully.")
    except docker.errors.APIError as e:
        print(f"Failed to pull image {image_name}:{tag}. Error : {e}")
