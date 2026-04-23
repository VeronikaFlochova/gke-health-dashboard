output "vpc_name" {
  description = "Name of the VPC"
  value       = module.vpc.vpc_name
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = module.vpc.subnet_name
}

output "gke_cluster_name" {
  description = "Name of the GKE cluster"
  value       = module.gke.gke_cluster_name
}
