# Deploying cvat in an Azure Kubernetes Service

This guide will focus on how to deploy cvat in an kubernetes environment.

## Requirements
You need to install 
- [kubectl](https://kubernetes.io/de/docs/tasks/tools/install-kubectl/)
- [nuctl](https://github.com/nuclio/nuclio/releases)
- [docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli)


## Building the container
In order to do so,
you will first need to build the cvat backend and frontend images.
Then push the builded images to a registry that the cluster has access to.
```bash
echo "Building backend"
cd ..
docker-compose build
```
## Push the Container to your Container Registry
At first you have to create your own Container Registry in Azure (ACR). You can
follow this guide to create one and make sure to create in the same ResourceGroup as your Azure Kubernetes Cluster.
https://docs.microsoft.com/de-de/azure/container-registry/container-registry-get-started-azure-cli.
```bash
az acr create --resource-group chaoskreuzung \
  --name labeling --sku Basic
```

You have to rename the container in this format `<login-server>/cvat`. You can
do this after the creation with `docker tag` or you rename the container
straightforward in the `docker-compose.yml` file.

After that you can login with `az acr login --name labeling` and you can push
all relevant container with `docker-compose push` to the registry.

## Create the Kubernetes Cluster in Azure

Create the Azure Kubernetes Cluster (AKS) with this command. You need
Subscription Owner Privileges to process this.
```bash
az aks create --resource-group <resource_group> --name <cluster_name> --node-count 1 --generate-ssh-keys --attach-acr <name_of_container_registry>
```
Now your AKS-Cluster has access to your ACR. Now it is able to pull the
pre-build Docker-Container from the Registry with Kubernetes. 

## Create a Static IP and a DNS Address 
https://docs.microsoft.com/de-de/azure/aks/ingress-tls

## Adjusting the kubernetes templates

1.  Replace the URL pointing to the backend and frontend image in
`kubernetes-templates/04_cvat_backend_deployment.yml` and
`kubernetes-templates/04_cvat_frontend_deployment.yml`.

2.  Insert your choosen database password the
`kubernetes-templates/02_database_secrets.yml`

## Deploying to the cluster
Deploy everything to your cluster with `kubectl apply -f .`

## Create the django super user

```bash
kubectl get pods --namespace cvat
kubectl --namespace cvat exec -it cvat-backend-78c954f84f-qxb8b -- /bin/bash
python3 ~/manage.py createsuperuser
```

## Deploy Nuclio for Autolabeling and Reidentification between Frames
[View here](../kubernetes-nuclio-templates/README.md)