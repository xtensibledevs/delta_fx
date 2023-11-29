import docker
import psutil
import requests
from docker.errors import APIError, DockerException

MANAGER_STAT_API_EP = ''

def create_swarm():
    try:
        client = docker.from_env()
        # initialize a new swarm
        swarm_init_result = client.swarm.init()
        # get the join token for worker nodes
        join_token_worker = swarm_init_result['JoinTokens']['Worker']
        # Get the join token for manager nodes
        join_token_manager = swarm_init_result['JoinTokens']['Manager']

        print("Swarm initalized successfully.")
        print("Worker Join Token : ", join_token_worker)
        print("Manager Join Token : ", join_token_manager)

    except APIError as api_error:
        print(f"Error while interacting with Docker API : {api_error}")
    except DockerException as docker_ex:
        print(f"Docker exception : {docker_ex}")
    except Exception as ex:
        print(f"An unexpected error occured : {ex}")

def get_system_info():
    cpu_cores = psutil.cpu_count(logical=True)

    # get total and available memory
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total
    available_memory = memory_info.available

    # get the disk space information
    disk_info = psutil.disk_usage('/')
    total_disk_space = disk_info.total
    free_disk_space = disk_info.free

    running_processes = []
    for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        running_processes.append({
            'pid': process.info['pid'],
            'name': process.info['name'],
            'cpu_percent': process.info['cpu_percent'],
            'memory_percent': process.info['memory_percent']
        })

    return {
        'cpu_cores': cpu_cores,
        'total_memory': total_memory,
        'available_memory': available_memory,
        'total_disk_space': total_disk_space,
        'free_disk_space': free_disk_space,
        'running_processes': running_processes
    }


def post_stats_to_api(stats):
    try:
        response = requests.post(MANAGER_STAT_API_EP, json=stats)

        if response.status_code == 200:
            print("Stats successfully posted to the API.")
        else:
            print(f"Failed to post stats to API. Status code : {response.status_code}")
            print("API Response:", response.text)
    except requests.RequestException as ex:
        print(f"Error while sending the request to the API : {ex}")


def initialize_worker_nodes(client, join_token_worker, manager_address):
    try:
        join_command_worker = f"docker swarm join --token {join_token_worker} {manager_address[0]}:{manager_address[1]}"
        result = client.containers.run("alpine", entrypoint=join_command_worker, remove=True)

        print(f"Worker nodes joined successfully:\n{result.decode('utf-8')}")
    except APIError as api_error:
        print(f"Error while interacting with Docker API : {api_error}")
    except DockerException as docker_ex:
        print(f"Docker exception : {docker_ex}")
    except Exception as ex:
        print(f"An unexpected error occured : {ex}")


def initialize_manager_nodes(client, join_token_manager):
    pass