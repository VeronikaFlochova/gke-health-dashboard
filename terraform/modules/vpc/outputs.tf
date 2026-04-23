output "vpc_name" {
    description = "Name of the VPC"
    value       = google_compute_network.vpc.name
}

output "subnet_name" {
    description = "Name of the subnet"
    value       = google_compute_subnetwork.subent.name
}

output "vpc_id" {
    description = "ID of the VPC"
    value       = google_compute_network.vpc.id
}
