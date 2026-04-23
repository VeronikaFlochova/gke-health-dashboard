from flask import Flask, render_template, jsonify
from kubernetes import client, config
import os
import datetime

# v1.1 - pipeline verification
app = Flask(__name__)

def get_kubernetes_client():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    return client.CoreV1Api()

def get_cluster_metrics():
    try:
        v1 = get_kubernetes_client()

        # Get nodes
        nodes = v1.list_node()
        node_data = []
        for node in nodes.items:
            conditions = {c.type: c.status for c in node.status.conditions}
            allocatable = node.status.allocatable
            capacity = node.status.capacity

            node_data.append({
                "name": node.metadata.name,
                "status": "Ready" if conditions.get("Ready") == "True" else "Not Ready",
                "cpu_allocatable": allocatable.get("cpu", "N/A"),
                "memory_allocatable": allocatable.get("memory", "N/A"),
                "cpu_capacity": capacity.get("cpu", "N/A"),
                "memory_capacity": capacity.get("memory", "N/A"),
                "created": node.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M") if node.metadata.creation_timestamp else "N/A"
            })

        # Get pods across all namespaces
        pods = v1.list_pod_for_all_namespaces()
        total_pods = len(pods.items)
        running_pods = sum(1 for p in pods.items if p.status.phase == "Running")
        pending_pods = sum(1 for p in pods.items if p.status.phase == "Pending")
        failed_pods = sum(1 for p in pods.items if p.status.phase == "Failed")

        # Get namespaces
        namespaces = v1.list_namespace()
        namespace_list = [ns.metadata.name for ns in namespaces.items]

        return {
            "nodes": node_data,
            "total_nodes": len(node_data),
            "healthy_nodes": sum(1 for n in node_data if n["status"] == "Ready"),
            "pods": {
                "total": total_pods,
                "running": running_pods,
                "pending": pending_pods,
                "failed": failed_pods
            },
            "namespaces": namespace_list,
            "total_namespaces": len(namespace_list),
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": None
        }

    except Exception as e:
        return {
            "nodes": [],
            "total_nodes": 0,
            "healthy_nodes": 0,
            "pods": {"total": 0, "running": 0, "pending": 0, "failed": 0},
            "namespaces": [],
            "total_namespaces": 0,
            "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

@app.route("/")
def index():
    metrics = get_cluster_metrics()
    return render_template("index.html", metrics=metrics)

@app.route("/api/metrics")
def api_metrics():
    return jsonify(get_cluster_metrics())

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)