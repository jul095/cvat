# Deploy Nuclio on AKS with CVAT

Nuclio is a serverless framework for machine learning Tasks. It's aim is to
provide a enviromnet like AWS Lambda for Machine Learning Tasks. 

In CVAT each model or automation function is deployed with nuclio. Each function
has a `function.yml` file for building the container and configure the runtime


## Requirements
- CVAT is deployed on AKS like explained [here](../kubernetes-templates/README.md)
- [kubectl](https://kubernetes.io/de/docs/tasks/tools/install-kubectl/)

## Deploy Nuclio on AKS
To deploy execute the command `kubectl apply -f .`
This will create the required pods in the `cvat` namespace. 

If you want to make the Dashboard accessable from public, you can change the 
`nuclio-dashboard-load-balancer` Service from ClusterIP to LoadBalancer.

You can follow https://nuclio.io/docs/latest/setup/aks/getting-started-aks/ to
get everything in detail.