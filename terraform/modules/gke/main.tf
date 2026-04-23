resource "google_container_cluster" "primary" {
  name     = var.gke_cluster_name
  project  = var.project_id
  location = var.zone

  network    = var.vpc_name
  subnetwork = var.subnet_name

  remove_default_node_pool = true
  initial_node_count       = 1

  deletion_protection = false
}

resource "google_container_node_pool" "primary_nodes" {
  name     = "${var.gke_cluster_name}-node-pool"
  project  = var.project_id
  location = var.zone
  cluster  = google_container_cluster.primary.name

  node_count = var.gke_num_nodes

  node_config {
    machine_type = var.gke_machine_type
    disk_size_gb = 20
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = {
      env     = "production"
      project = var.project_id
    }

    tags = ["gke-node", var.gke_cluster_name]
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}