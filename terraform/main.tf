terraform {
  required_version = ">= 1.0"

  backend "gcs" {
    bucket = "tfstate-veronika-gke"
    prefix = "gke-health-dashboard"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

module "vpc" {
  source      = "./modules/vpc"
  project_id  = var.project_id
  region      = var.region
  vpc_name    = var.vpc_name
  subnet_name = var.subnet_name
  subnet_cidr = var.subnet_cidr
}

module "gke" {
  source           = "./modules/gke"
  project_id       = var.project_id
  region           = var.region
  zone             = var.zone
  gke_cluster_name = var.gke_cluster_name
  gke_num_nodes    = var.gke_num_nodes
  gke_machine_type = var.gke_machine_type
  vpc_name         = module.vpc.vpc_name
  subnet_name      = module.vpc.subnet_name
}