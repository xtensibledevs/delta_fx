Setting up a Docker cluster using Docker Swarm involves configuring a group of Docker hosts to work together. Docker Swarm provides native clustering and orchestration for Docker. Below are the basic steps to set up a Docker Swarm cluster:

### Prerequisites:

- Docker installed on all machines you want to include in the cluster.
- Network connectivity between the machines.
- The machines should have unique hostnames and a shared subnet.

### Architecture

### Steps:

1. **Initialize the Swarm on Manager Node:**

   Choose one of the machines to be the manager node (leader) and initialize the Swarm:

   ```bash
   docker swarm init --advertise-addr <MANAGER-IP>
   ```

   Note the command output, as it contains the command to join worker nodes to the Swarm.

2. **Join Worker Nodes:**

   On each machine you want to join as a worker node, run the command obtained from the `docker swarm init` output on the manager:

   ```bash
   docker swarm join --token <TOKEN> <MANAGER-IP>:<PORT>
   ```

   Replace `<TOKEN>`, `<MANAGER-IP>`, and `<PORT>` with the values obtained from the manager.

3. **Check Swarm Status:**

   On the manager node, check the status of the Swarm:

   ```bash
   docker node ls
   ```

   This command should list all nodes in the Swarm, with one node marked as the leader (manager) and the others as workers.

4. **Deploy Services:**

   Use Docker Compose or the `docker service` command to deploy services to the Swarm. For example:

   ```bash
   docker service create --replicas 3 -p 80:80 --name web nginx
   ```

   This command deploys an Nginx service with three replicas across the cluster.

5. **Check Service Status:**

   Monitor the status of the deployed services:

   ```bash
   docker service ls
   ```

   This command lists all services in the Swarm along with their status.

6. **Scale Services:**

   Adjust the number of replicas for a service:

   ```bash
   docker service scale web=5
   ```

   This command scales the `web` service to have five replicas.

7. **Update Services:**

   Update a service with a new image or configuration:

   ```bash
   docker service update --image new-image:tag web
   ```

   This command updates the `web` service to use a new image.

8. **Drain and Remove Nodes (Optional):**

   If you need to take a node out of service, use the `docker node update` command with the `--availability` flag. For example, to drain a node:

   ```bash
   docker node update --availability drain <NODE-ID>
   ```

   To remove a node:

   ```bash
   docker node rm <NODE-ID>
   ```

### Additional Tips:

- **Visualizing the Swarm:**
  You can use tools like [Portainer](https://www.portainer.io/) or the built-in Docker Swarm visualizer for a graphical representation of your Swarm.

- **Secure Your Swarm:**
  Ensure that your Swarm is secured. Use TLS certificates for communication and protect access to your Docker API.

This is a basic setup, and depending on your requirements, you might want to explore additional Swarm features like secrets management, rolling updates, etc. Always refer to the [official Docker Swarm documentation](https://docs.docker.com/swarm/) for the most up-to-date and detailed information.