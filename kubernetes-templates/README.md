# Deploying cvat in an Azure Kubernetes Service

This guide will focus on how to deploy cvat in an kubernetes environment.

## Requirements


## Building the container
In order to do so,
you will first need to build the cvat backend and frontend images.
Then push the builded images to a registry that the cluster has access to.
```bash
echo "Building backend"
cd ..
docker-compose push
```

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
