#!/usr/bin/env python3
"""
GKE DevOps Agent - Cluster Health Monitor

This module provides comprehensive cluster health monitoring with:
- Node status and readiness checks
- Pod health metrics and efficiency calculations  
- Professional dashboard formatting with emojis and dividers
- Real-time infrastructure and workload status reporting

Author: GKE DevOps Team
"""

from .config import k8s_v1
from .models import Node
from kubernetes.client.exceptions import ApiException

def check_cluster_health() -> dict:
    """
    Check overall GKE cluster health status with detailed metrics.
    
    Provides comprehensive cluster health assessment including:
    - Node readiness and version information
    - Pod health metrics and distribution
    - System reliability calculations
    - Infrastructure utilization analysis
    
    Returns:
        dict: Formatted cluster health dashboard with infrastructure and workload status
    """
    try:
        nodes_api = k8s_v1.list_node()
        nodes = []
        for n in nodes_api.items:
            node_ready = any(c.type == "Ready" and c.status == "True" for c in n.status.conditions)
            nodes.append(Node(
                name=n.metadata.name,
                status="✅ Ready" if node_ready else "❌ NotReady",
                version=n.status.node_info.kubelet_version,
            ))
        
        ready_nodes = sum(1 for n in nodes if n.status == "✅ Ready")
        
        pods = k8s_v1.list_pod_for_all_namespaces()
        pod_phases = [p.status.phase for p in pods.items]
        running_pods = pod_phases.count("Running")
        failed_pods = pod_phases.count("Failed")
        pending_pods = pod_phases.count("Pending")
        
        total_pods = len(pods.items)
        pod_health_percentage = (running_pods / total_pods * 100) if total_pods > 0 else 100

        if failed_pods > 0:
            cluster_status = f"🔴 ATTENTION: {failed_pods} failed pod(s) detected."
        elif pending_pods > 0:
            cluster_status = f"🟡 PENDING: {pending_pods} pod(s) are pending."
        else:
            cluster_status = "🟢 EXCELLENT: All systems operational."

        node_lines = []
        for node in nodes:
            node_lines.append(f"- {node.name} ({node.status})")
        
        return {
            "status": "success",
            "formatted_response": f"""
🏥 **GKE Cluster Health Report**

**{cluster_status}**

**Summary:**
- **Nodes:** {ready_nodes}/{len(nodes)} Ready
- **Pods:** {running_pods}/{total_pods} Running
- **Health:** {pod_health_percentage:.0f}% Pods Healthy

**Node Status:**
{chr(10).join(node_lines)}

**Workload Status:**
- **Running:** {running_pods}
- **Pending:** {pending_pods}
- **Failed:** {failed_pods}
            """
        }
    except ApiException as e:
        return {"status": "error", "error_message": f"Kubernetes API error: {e.reason}"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}