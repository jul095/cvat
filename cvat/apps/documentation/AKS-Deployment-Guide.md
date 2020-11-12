
# Deployment on Azure Kubernetes Services
- [Deploy CVAT](#Deploying-CVAT-on-Azure-Kubernetes-Service)
- [Activate SSL and DNS Domain with Ingress](#Ingress-SSL-and-DNS)
- [Nuclio](#Nuclio)

## Deploying CVAT on Azure Kubernetes Service

This guide will focus on how to deploy cvat in an kubernetes environment.

### Requirements
You need to install 
- [kubectl](https://kubernetes.io/de/docs/tasks/tools/install-kubectl/)
- [nuctl](https://github.com/nuclio/nuclio/releases)
- [docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli)


### Building the container
In order to do so,
you will first need to build the cvat backend and frontend images.
Then push the builded images to a registry that the cluster has access to. Run
following command in the root folder of this Repository.
```bash
docker-compose build
```
### Push the Container to your Container Registry
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

### Create the Kubernetes Cluster in Azure

Create the Azure Kubernetes Cluster (AKS) with this command. You need
Subscription Owner Privileges to run this.
```bash
az aks create --resource-group <resource_group> --name <cluster_name> --node-count 1 --generate-ssh-keys --attach-acr <name_of_container_registry>
```
Now your AKS-Cluster has access to your ACR. Now it is able to pull the
pre-build Docker-Container from the Registry with Kubernetes. 

### Create a Static IP and a DNS Address 
https://docs.microsoft.com/de-de/azure/aks/ingress-tls

### Adjusting the kubernetes templates

1.  Replace the URL pointing to the backend and frontend image in
`kubernetes-templates/04_cvat_backend_deployment.yml` and
`kubernetes-templates/04_cvat_frontend_deployment.yml`.

2.  Insert your choosen database password the
`kubernetes-templates/02_database_secrets.yml`

### Deploying to the cluster
Deploy everything to your cluster with `kubectl apply -f .`

### Create the django super user

```bash
kubectl get pods --namespace cvat
kubectl --namespace cvat exec -it cvat-backend-78c954f84f-qxb8b -- /bin/bash
python3 ~/manage.py createsuperuser
```

## Ingress SSL and DNS

Ingress is responsible for managing HTTP and HTTPS Traffic from outside the
cluster to services within the cluster. With the K8s load balancer type alone
it's not possible to host with ssl encryption. So it's necessary to provide a
ingress configuration. 

### Requirements
- [helm](https://helm.sh/docs/intro/install/)

### Create a static Public IP with DNS Address
At first create a static IP with this command. The sku is important. If you have
a standard load balancer in AKS, you must use Standard here as well.

```bash
az network public-ip create \                                                                            
    --resource-group <resourceGroup> \
    --name <name_of_ip_address> \
    --sku Standard 
```
To Access the IP from your AKS-Service, you need to add the `Network
Contributor` role to your
responsible AKS Service Principal.

You can get the necessary data with following commands. 
- SP_Client_ID: in the UI in the main AKS page of the cluster
- subscription_id: `az account list --output table

```bash
az role assignment create \
    --assignee <SP Client ID> \
    --role "Network Contributor" \
    --scope /subscriptions/<subscription id>/resourceGroups/<resource group name>
```

Now you can run following Bash script provided by Microsoft to attach a DNS
Label to this IP Address
```bash
# Public IP address of your ingress controller
IP="MY_EXTERNAL_IP"

# Name to associate with public IP address
DNSNAME="demo-aks-ingress"

# Get the resource-id of the public ip
PUBLICIPID=$(az network public-ip list --query "[?ipAddress!=null]|[?contains(ipAddress, '$IP')].[id]" --output tsv)

# Update public ip address with DNS name
az network public-ip update --ids $PUBLICIPID --dns-name $DNSNAME

# Display the FQDN
az network public-ip show --ids $PUBLICIPID --query "[dnsSettings.fqdn]" --output tsv
```

Now you have to install the cert-manager to use Let's Encrypt for a
TLS-Certificate.
```bash
# Add the Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io

# Update your local Helm chart repository cache
helm repo update

# Install the cert-manager Helm chart
helm install \
  cert-manager \
  --namespace cvat \
  --version v0.16.1 \
  --set installCRDs=true \
  --set nodeSelector."beta\.kubernetes\.io/os"=linux \
  jetstack/cert-manager
```

The cert-manager needs a Issuer and some data. You have to apply it to your
kubernetes cluster. Take care to provide a email from your Organisation. This
will remind you if you need to update the certificate.
```yaml
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: MY_EMAIL_ADDRESS
    privateKeySecretRef:
      name: letsencrypt
    solvers:
    - http01:
        ingress:
          class: nginx
          podTemplate:
            spec:
              nodeSelector:
                "kubernetes.io/os": linux
```
Details: https://docs.microsoft.com/de-de/azure/aks/static-ip

### Add Ingress to AKS Cluster

At first add the nginx-ingress Repository to helm `helm repo add ingress-nginx
https://kubernetes.github.io/ingress-nginx`

After that you can add ingress-nginx to your cluster. You can add the
`replicaCount` for your purposes.

```bash
helm install nginx-ingress ingress-nginx/ingress-nginx \
    --namespace cvat \
    --set controller.replicaCount=1 \
    --set controller.nodeSelector."beta\.kubernetes\.io/os"=linux \
    --set defaultBackend.nodeSelector."beta\.kubernetes\.io/os"=linux \
    --set controller.service.loadBalancerIP="Created Static IP Address" \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-dns-label-name"="<Your created DNS-Label>"\
 --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-resource-group"="<Your Resource Group of the DNS Label>"
```

Now you can update and deploy the [Ingress
Configuration](../../../kubernetes-templates/07_labeling_ingress.yml)
`07_labeling_ingress.yml` in the
[kubernetes-templates](../../../kubernetes-templates) folder. Just change the
`hosts` and `host` with your domain from Azure. The structure is for example
`<dsnLabel>.westeurope.cloudapp.azure.com`

Deploy it with `kubectl apply -f 07_labeling_ingress.yml` and there you go :yum:

Details: https://docs.microsoft.com/de-de/azure/aks/ingress-tls


## Nuclio

Nuclio is a serverless framework for machine learning Tasks. It's aim is to
provide a enviromnet like AWS Lambda for Machine Learning Tasks. 

In CVAT each model or automation function is deployed with nuclio. Each function
has a `function.yml` file for building the container and configure the runtime


### Requirements
- CVAT is deployed on AKS like explained [here](../kubernetes-templates/README.md)
- [kubectl](https://kubernetes.io/de/docs/tasks/tools/install-kubectl/)

### Deploy Nuclio on AKS
The required config files are in the root
[kubernetes-nuclio-templates](../../../kubernetes-nuclio-templates) folder. So
`cd` in this directory.
To deploy execute the command `kubectl apply -f .`
This will create the required pods in the `cvat` namespace. 

If you want to make the Dashboard accessable from public, you can change the 
`nuclio-dashboard-load-balancer` Service from ClusterIP to LoadBalancer.

You can follow https://nuclio.io/docs/latest/setup/aks/getting-started-aks/ to
get everything in detail.


## Deploy Nuclio Functions

### Requirements
- [Deployed CVAT](#Deploying-CVAT-on-Azure-Kubernetes-Service) on Kubernetes AKS
- [nuctl](https://github.com/nuclio/nuclio/releases)
- [docker](https://docs.docker.com/engine/install/)
- [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli)
- Signed in with AzureCLI and your Kubernetes Cluster is accessable with `kubectl`

### Create a project
At first create a project for cvat `nuctl create project cvat --platform kube --namespace cvat`

### Build container
If you want to build the container just execute this command.
```bash
nuctl build nuclio-polygon-reidentification --path serverless/polygon-reidentification/nuclio --registry <ACR_REGISTRY>
```
If you deploy locally it is not necessary to build the container before
deployment. But in the cluster you don't have access to you local file system so
it's easier to build a flexible container using the build-specs in the
`function.yml` and deploy this in the next step on AKS.

### Deploy container
To deploy a nuclio container from the Container Registry you can use this
command. Take care of namespace and project name. CVAT has a project filter in
the backend. You can change the Namespace to a different one. Just change the
Kubernetes-Files in the
[kubernetes-nuclio-templates](../../../kubernetes-nuclio-templates) folder.

```bash
nuctl deploy polygon-reidentifcation --run-image labeling.azurecr.io/polygon-reidentification -f serverless/polygon-reidentification/nuclio/function.yaml --namespace cvat --project-name cvat --platform kube
```
Now you should be able to access the serverless function with CVAT.



