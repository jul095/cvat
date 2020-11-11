## Deploy a model and helper function on AKS


## Requirements
- Deployed Nuclio on Kubernetes AKS
- [nuctl](https://github.com/nuclio/nuclio/releases)
- [docker](https://docs.docker.com/engine/install/)
- [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli)
- Signed in with AzureCLI and your Kubernetes Cluster is accessable with `kubectl`

## Create a project
At first create a project for cvat `nuctl create project cvat --platform kube --namespace cvat`

## Build container
If you want to build the container just execute this command.
```bash
nuctl build nuclio-polygon-reidentification --path polygon-reidentification/nuclio --registry <ACR_REGISTRY>
```
If you deploy locally it is not necessary to build the container before
deployment. But in the cluster you don't have access to you local file system so
it's easier to build a flexible container using the build-specs in the
`function.yml` and deploy this in the next step on AKS.

## Deploy container
To deploy a nuclio container from the Container Registry you can use this
command. Take care of namespace and project name. CVAT has a project filter in
the backend.
```bash
nuctl deploy polygon-reidentifcation --run-image labeling.azurecr.io/polygon-reidentification -f serverless/polygon-reidentification/nuclio/function.yaml --namespace cvat --project-name cvat
```
Now you should be able to access the serverless function with CVAT.


