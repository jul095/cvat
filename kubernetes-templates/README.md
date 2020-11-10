# Deploying cvat in an Azure Kubernetes Service

This guide will focus on how to deploy cvat in an kubernetes environment.

## Requirements
You need to install 
- nuctl
- kubectl
- docker
- docker-compose

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



## Adjusting the kubernetes templates

1.  Replace the URL pointing to the backend and frontend image in
`kubernetes-templates/04_cvat_backend_deployment.yml` and
`kubernetes-templates/04_cvat_frontend_deployment.yml`.
Furthermore, adjusting their pull secrets or remove the lines accordingly.

1.  Replacing the domain dummy with your real domain name
`cvat.my.cool.domain.com`.
Replace `{MY_SERVER_URL_COM}` in
`kubernetes-templates/04_cvat_frontend_deployment.yml` and
`kubernetes-templates/05_cvat_proxy_configmap.yml`.

1.  Insert your choosen database password the
`kubernetes-templates/02_database_secrets.yml`

## Deploying to the cluster
Deploy everything to your cluster with `kubectl apply -f kubernetes-templates/`

## Create the django super user

```bash
kubectl get pods --namespace cvat
kubectl --namespace cvat exec -it cvat-backend-78c954f84f-qxb8b -- /bin/bash
python3 ~/manage.py createsuperuser
```
