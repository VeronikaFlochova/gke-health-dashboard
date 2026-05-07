# GKE Health Dashboard
### Production-Ready GCP Architecture | End-to-End Cloud System

![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Cloud Build](https://img.shields.io/badge/Cloud_Build-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## Overview

This project demonstrates how to design, deploy, and manage a production-style cloud system on Google Cloud. The goal was to build a complete, connected system — not four separate exercises — where infrastructure is automated, the application is containerised, deployments are fully streamlined, and the system is observable in real time.

The app is a real-time GKE Health Dashboard that pulls live metrics from a running cluster and displays them through a Flask web interface: node status, pod health, and resource utilisation per node.

**Live app:** http://34.147.179.233

> 📹 **2-minute walkthrough:** [Watch on Loom →](#) *(replace # with your Loom link)*

---

## Architecture

```
GitHub Push
    |
    v
Cloud Build Trigger
    |
    |-- Build Docker image
    |-- Push to Artifact Registry
    |-- Deploy to GKE via kubectl
              |
              v
     GKE Cluster (europe-west2)
     cloudeng-cluster, 2 nodes
              |
              v
     Flask App behind Load Balancer
     http://34.147.179.233
              |
              v
     Cloud Monitoring
     Uptime checks and alerting policies
```

---

## Stack

| Layer | Tool |
|---|---|
| Infrastructure | Terraform |
| Cluster | GKE (Kubernetes) |
| Container Registry | Google Artifact Registry |
| CI/CD | Google Cloud Build |
| Application | Python · Flask |
| Monitoring | Google Cloud Monitoring |

---

## Project Structure

```
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
```

---

## Infrastructure

Provisioned with Terraform, organised into two modules.

The **VPC module** creates a custom VPC with a dedicated subnet in europe-west2 and firewall rules scoped to required traffic only. Nothing runs in the default network.

The **GKE module** provisions a two-node cluster with a dedicated node pool inside the custom VPC.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Application

The Flask app connects to the Kubernetes API using in-cluster credentials and displays:

- Node count and status
- Pod health per namespace
- CPU and memory allocatable per node

RBAC is configured to give the app read-only access to cluster resources.

---

## CI/CD

Every push to main triggers the pipeline automatically via a Cloud Build trigger connected to GitHub. No manual deployment steps are required after initial setup.

Pipeline steps defined in `cloudbuild.yaml`:

1. Build the Docker image
2. Push to Artifact Registry tagged with the commit SHA
3. Authenticate against the GKE cluster
4. Deploy with kubectl

---

## Monitoring

Configured via GCP Cloud Monitoring console:

- **Uptime check** — pings the load balancer every 5 minutes from multiple regions. Email alert fires if the app stops responding.
- **CPU alerting policy** — triggers an email if node CPU utilisation goes above 80% for more than 5 minutes.

> Monitoring is intentionally configured via console to validate alerting behaviour before codifying. In a team environment these policies would be moved into Terraform once stable.

---

## Design Decisions

**Custom VPC rather than the default network.**
The default GCP network has overly permissive firewall rules and is shared across services. A custom VPC gives explicit control over what traffic is allowed and where.

**Artifact Registry rather than Container Registry.**
Container Registry is deprecated on GCP. Artifact Registry is the current standard and has proper IAM support.

**Commit SHA image tags.**
Each build is tagged with its Git commit SHA so you can trace exactly what is running in the cluster back to the commit that produced it.

**Read-only RBAC for the app.**
The dashboard only reads cluster state. There is no reason for it to have write access, so it does not have it.

---

## Running It Yourself

**Prerequisites:**
- GCP project with billing enabled
- gcloud CLI installed and authenticated
- Terraform installed
- kubectl installed
- Docker installed

```bash
# Clone the repo
git clone https://github.com/VeronikaFlochova/gke-health-dashboard
cd gke-health-dashboard

# Provision infrastructure
cd terraform
terraform init && terraform apply

# Authenticate gcloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Connect kubectl to the cluster
gcloud container clusters get-credentials cloudeng-cluster \
  --zone europe-west2-a \
  --project YOUR_PROJECT_ID

# Deploy the app
kubectl apply -f k8s/

# Get the external IP
kubectl get service
```

---

## Author

**Veronika Flochova** · Cloud Engineer · Google Certified Associate Cloud Engineer
📍 London, UK

[GitHub](https://github.com/VeronikaFlochova) · [LinkedIn](https://www.linkedin.com/in/veronikaflochova/) · 
*Currently advancing towards Professional Cloud Architect certification.*
