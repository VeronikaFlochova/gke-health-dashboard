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

This project demonstrates how to design, deploy, and manage a production-style cloud system on Google Cloud. The goal was to build a complete, connected system rather than four separate exercises, where infrastructure is automated, the application is containerised, deployments are fully streamlined, and the system is observable in real time.

The app is a real-time GKE Health Dashboard that pulls live metrics from a running cluster and displays them through a Flask web interface: node status, pod health, and resource utilisation per node.

**Live app:** http://34.147.179.233

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
    |-- Substitute image tag into manifests
    |-- Apply manifests and wait for rollout
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
| State | Google Cloud Storage, versioned |
| Cluster | GKE (Kubernetes) |
| Container Registry | Google Artifact Registry |
| CI/CD | Google Cloud Build |
| Application | Python, Flask |
| Monitoring | Google Cloud Monitoring |

---

## Project Structure

```
cloudeng-project/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   └── modules/
│       ├── vpc/
│       └── gke/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
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

The **VPC module** creates a custom VPC with a dedicated subnet in europe-west2 and firewall rules scoped by target tag to the cluster nodes. Nothing runs in the default network.

The **GKE module** provisions a two-node cluster with a dedicated node pool inside the custom VPC. The default node pool is removed and replaced with a managed one, so node configuration is explicit rather than inherited.

State is held in a versioned Cloud Storage bucket rather than locally, so the project can be worked on from more than one machine and a corrupted state file can be rolled back.

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

---

## Security

**Container.** The image creates an unprivileged user and switches to it after installing dependencies, so the application does not run as root. The pod spec enforces this with `runAsNonRoot` and `runAsUser`, so a future change that removed the user from the image would fail to start rather than silently running as root.

**Runtime.** The container filesystem is read only, with a single writable `emptyDir` mounted at `/tmp` for temporary files. All Linux capabilities are dropped, privilege escalation is disabled, and the default seccomp profile is applied.

**Kubernetes access.** The dashboard uses a dedicated ServiceAccount bound to a ClusterRole limited to `get`, `list` and `watch` on nodes, pods, namespaces and services. It has no write access to anything.

**Network.** Firewall rules are scoped with `target_tags` to the cluster nodes rather than applying to every resource in the VPC. Ports 80 and 443 accept traffic from any source because this is a public web application; the internal rule is restricted to the subnet CIDR.

### Known limitations

These are understood rather than overlooked, and are recorded here rather than left for someone to find.

**Node service account.** Nodes run as the default Compute Engine service account with `cloud-platform` scope. That account is scoped to five roles rather than Editor, so the exposure is bounded, but the correct design is a dedicated node service account with minimal roles plus Workload Identity so that pods hold their own identity rather than borrowing the node's.

**No NetworkPolicy.** Any pod can reach any other pod. With a single workload this is theoretical, but a multi-workload cluster would need default-deny policies.

**Single zone.** The cluster runs in `europe-west2-a`. A zone failure takes it down. A regional cluster would fix this at roughly double the node cost.

**No TLS.** The application is served over HTTP through a Service of type LoadBalancer. Production would use an Ingress with a Google-managed certificate and a real hostname.

---

## CI/CD

Every push to main triggers the pipeline automatically via a Cloud Build trigger connected to GitHub.

Pipeline steps defined in `cloudbuild.yaml`:

1. Build the Docker image
2. Push to Artifact Registry tagged with the commit SHA
3. Substitute the project ID and image tag into the Kubernetes manifests
4. Authenticate against the cluster, apply all manifests, and wait for the rollout to complete

Step 4 waits deliberately. `kubectl apply` returns as soon as the cluster accepts the change, so without `kubectl rollout status` a build reports success even when every new pod fails to start. The build now fails if the new pods do not become healthy within the timeout.

---

## Monitoring

Configured via GCP Cloud Monitoring console:

- **Uptime check** pings the load balancer every 5 minutes from multiple regions. Email alert fires if the app stops responding.
- **CPU alerting policy** triggers an email if node CPU utilisation goes above 80% for more than 5 minutes.

> Monitoring is intentionally configured via console to validate alerting behaviour before codifying. In a team environment these policies would be moved into Terraform once stable.

---

## Design Decisions

**Custom VPC rather than the default network.**
The default GCP network has overly permissive firewall rules and is shared across services. A custom VPC gives explicit control over what traffic is allowed and where.

**Firewall rules scoped by target tag.**
A rule with no `target_tags` applies to every resource in the network. Scoping to the `gke-node` tag means the rules cover the nodes that need them and nothing else, including anything added to the VPC later.

**Artifact Registry rather than Container Registry.**
Container Registry is deprecated on GCP. Artifact Registry is the current standard and has proper IAM support.

**Commit SHA image tags, and manifests as the source of truth.**
Each build is tagged with its Git commit SHA so you can trace exactly what is running back to the commit that produced it. The manifest holds a placeholder that the pipeline substitutes, rather than the pipeline patching the cluster directly with `kubectl set image`. That keeps the file in Git describing what actually runs, and means changes to RBAC or the Service ship with the deploy instead of sitting in Git doing nothing.

**Read-only RBAC for the app.**
The dashboard only reads cluster state. There is no reason for it to have write access, so it does not have it.

**Non-root container.**
By default a container runs as root, so any flaw in the application starts from a privileged position. Running as an unprivileged user with a read only filesystem removes a step from that chain for the cost of two lines in the Dockerfile.

**`moved` blocks rather than `terraform state mv` for renames.**
A resource rename changes Terraform's internal address, so without help Terraform plans to destroy and recreate. `terraform state mv` fixes that on one machine and leaves no record. A `moved` block lives in the code, appears in the diff, and gives anyone cloning the repo the same behaviour.

---

## Running It Yourself

**Prerequisites:**
- GCP project with billing enabled
- gcloud CLI installed and authenticated
- Terraform installed
- kubectl installed

```bash
# Clone the repo
git clone https://github.com/VeronikaFlochova/gke-health-dashboard
cd gke-health-dashboard

# Authenticate and set your project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Provide your project ID
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# edit terraform.tfvars and set project_id

# Provision infrastructure
cd terraform
terraform init && terraform apply
cd ..

# Connect kubectl to the cluster
gcloud container clusters get-credentials cloudeng-cluster \
  --zone europe-west2-a \
  --project YOUR_PROJECT_ID

# Build and deploy through the pipeline
gcloud builds submit --config cloudbuild.yaml

# Get the external IP
kubectl get service
```

> The manifests in `k8s/` contain `__PROJECT_ID__` and `__IMAGE_TAG__` placeholders that the pipeline substitutes at build time, so `kubectl apply -f k8s/` will not work on its own. Deployment goes through Cloud Build, which is what keeps the manifests in Git and the running cluster in agreement.

---

## Author

**Veronika Flochova** · Cloud Architect and Cloud Engineer · Google Certified Professional Cloud Architect and Associate Cloud Engineer
📍 London, UK

[GitHub](https://github.com/VeronikaFlochova) · [LinkedIn](https://www.linkedin.com/in/veronikaflochova/)

