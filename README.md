GKE Health Dashboard
A cloud engineering project built on Google Cloud Platform. Infrastructure is provisioned with Terraform, the application runs on Kubernetes, and every deployment is handled automatically by Cloud Build on push to main.
Live app: http://34.39.26.187

What it does
The app is a real-time dashboard that pulls live metrics from a running GKE cluster and displays them through a Flask web interface — node status, pod health, and resource utilisation per node.

Architecture
GitHub Push
    │
    ▼
Cloud Build Trigger
    │
    ├── Build Docker image
    ├── Push to Artifact Registry
    └── Deploy to GKE via kubectl
              │
              ▼
     GKE Cluster (europe-west2)
     cloudeng-cluster — 2 nodes
              │
              ▼
     Flask App (Load Balancer)
     http://34.39.26.187
              │
              ▼
     Cloud Monitoring
     Uptime checks + alerting policies

Stack
LayerToolInfrastructureTerraformClusterGKE (Kubernetes)Container registryGoogle Artifact RegistryCI/CDGoogle Cloud BuildApplicationPython, FlaskMonitoringGoogle Cloud Monitoring

Project structure
cloudeng-project/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── modules/
│       ├── vpc/
│       └── gke/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/
│       └── index.html
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── rbac.yaml
└── cloudbuild.yaml

Infrastructure
Provisioned with Terraform, split into two modules.
VPC module — custom VPC with a dedicated subnet in europe-west2 and firewall rules scoped to required traffic only. Nothing runs in the default network.
GKE module — two-node cluster with a dedicated node pool, sitting inside the custom VPC.
bashcd terraform
terraform init
terraform plan
terraform apply

Application
The Flask app connects to the Kubernetes API using in-cluster credentials and displays:

Node count and status
Pod health per namespace
CPU and memory allocatable per node

RBAC is configured to give the app read-only access to cluster resources.

CI/CD
Every push to main triggers the pipeline automatically. Cloud Build authenticates against the GKE cluster and applies the updated deployment — no manual steps after initial setup.
Pipeline steps defined in cloudbuild.yaml:

Build Docker image
Push to Artifact Registry, tagged with the commit SHA
Authenticate against GKE
Deploy with kubectl


Monitoring
Uptime check — pings the load balancer every 5 minutes from multiple regions. Sends an email alert if the app stops responding.
CPU alert — triggers an email if node CPU utilisation goes above 80% for more than 5 minutes.

Running it yourself
Prerequisites

GCP project with billing enabled
gcloud CLI authenticated
Terraform installed
kubectl installed
Docker installed

Steps
bash# Clone the repo
git clone https://github.com/VeronikaFlochova/gke-health-dashboard
cd gke-health-dashboard

# Provision infrastructure
cd terraform
terraform init && terraform apply

# Connect kubectl to the cluster
gcloud container clusters get-credentials cloudeng-cluster \
  --zone europe-west2-a \
  --project YOUR_PROJECT_ID

# Deploy the app
kubectl apply -f k8s/

# Get the external IP
kubectl get service -n default

A few decisions worth explaining
Custom VPC — the default GCP network has overly permissive firewall rules and is shared across services. A custom VPC gives explicit control over what traffic is allowed and where.
Artifact Registry over Container Registry — Container Registry is deprecated on GCP. Artifact Registry is the current standard and has proper IAM support.
Commit SHA image tags — each build is tagged with its Git commit SHA so you can trace exactly what is running in the cluster back to the commit that produced it.
Read-only RBAC — the dashboard only reads cluster state. There is no reason for it to have write access, so it does not have it.

Author
Veronika Flochova
[GitHub](https://github.com/VeronikaFlochova) · [LinkedIn](https://www.linkedin.com/in/veronikaflochova/)